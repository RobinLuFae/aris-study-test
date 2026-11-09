"""Post-training tabulation of WITT's scalar-only SNR modulators."""
import torch
from torch import nn


class SNRGateTable(nn.Module):
    def __init__(self, knots, values, interpolation='linear'):
        super().__init__()
        if interpolation not in ('linear', 'nearest'):
            raise ValueError('Unknown interpolation')
        if knots.ndim != 1 or len(knots) < 2 or values.shape[0] != len(knots):
            raise ValueError('Expected K knots and K-by-M gate values')
        steps = knots[1:]-knots[:-1]
        if not torch.all(steps > 0) or not torch.allclose(steps, steps[0].expand_as(steps)):
            raise ValueError('This implementation requires strictly increasing uniform knots')
        self.register_buffer('knots', knots.detach().clone())
        self.register_buffer('values', values.detach().clone())
        self.interpolation = interpolation

    def forward(self, snr):
        # The deployment domain is explicitly bounded; clamp outside the table interval.
        position = (snr.squeeze(-1).clamp(self.knots[0], self.knots[-1])-self.knots[0])
        position = position / (self.knots[1]-self.knots[0])
        if self.interpolation == 'nearest':
            return self.values[position.round().long().clamp(0, len(self.knots)-1)]
        lower = position.floor().long().clamp(0, len(self.knots)-1)
        upper = (lower+1).clamp(max=len(self.knots)-1)
        fraction = (position-lower).unsqueeze(-1)
        return self.values[lower]+fraction*(self.values[upper]-self.values[lower])


class SharedSNRModulator(nn.Module):
    """Exact uniform-SNR computation control; keeps the entire original MLP."""
    def __init__(self, original):
        super().__init__()
        self.original = original

    def forward(self, snr):
        # Author WITT expands one scalar SNR across the whole batch.
        return self.original(snr[:1]).expand(snr.shape[0], -1)


def share_snr_computation(model):
    for side in ('encoder', 'decoder'):
        branch = getattr(model, side)
        for i, original in enumerate(branch.bm_list):
            branch.bm_list[i] = SharedSNRModulator(original)


def install_empty_tables(model, anchors, interpolation):
    """Construct the deployment shape before strictly loading a saved table state."""
    for side in ('encoder', 'decoder'):
        branch = getattr(model, side)
        for i, original in enumerate(branch.bm_list):
            param = next(original.parameters())
            knots = torch.linspace(1., 13., anchors, device=param.device, dtype=param.dtype)
            width = original.fc[-2].out_features
            branch.bm_list[i] = SNRGateTable(knots, torch.zeros(anchors, width, device=param.device), interpolation)


@torch.no_grad()
def tabulate_snr_gates(model, anchors, interpolation='linear'):
    """Replace the modules, removing all of their Parameters from this model."""
    if anchors < 2:
        raise ValueError('At least two anchors required')
    before = sum(p.numel() for p in model.parameters())
    rows = []
    for side in ('encoder', 'decoder'):
        branch = getattr(model, side)
        for index, original in enumerate(branch.bm_list):
            param = next(original.parameters())
            knots = torch.linspace(1., 13., anchors, device=param.device, dtype=param.dtype)
            values = original(knots[:, None])
            table = SNRGateTable(knots, values, interpolation)
            # Check a dense scalar grid on the current device (CPU during preparation).
            grid = torch.linspace(1., 13., 97, device=param.device, dtype=param.dtype)[:, None]
            error = table(grid)-original(grid)
            rows.append({'side': side, 'index': index,
                         'removed_parameters': sum(p.numel() for p in original.parameters()),
                         'gate_values': values.numel(), 'knot_values': knots.numel(),
                         'dense_grid_max_abs_gate_error': error.abs().max().item(),
                         'dense_grid_rms_gate_error': error.square().mean().sqrt().item()})
            branch.bm_list[index] = table
    after = sum(p.numel() for p in model.parameters())
    return {'anchors': anchors, 'interpolation': interpolation,
            'parameter_count_before': before, 'parameter_count_after': after,
            'removed_parameter_count': before-after,
            'table_gate_values': sum(r['gate_values'] for r in rows),
            'table_knot_values': sum(r['knot_values'] for r in rows),
            'modules': rows,
            'scope': 'Post-training deployment transformation; image-dependent sm_list and backbone retained.'}
