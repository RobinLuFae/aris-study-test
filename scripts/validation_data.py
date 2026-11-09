"""Read an already-frozen validation split without opening test images or test MD5s."""
import json
import torch
import torchvision
from witt_support import ROOT


class TrainingPartitionOnly(torchvision.datasets.CIFAR10):
    test_list = []


def frozen_validation(config, samples):
    split_file = ROOT/'data/splits'/f"cifar10_seed{config['split_seed']}_val{config['validation_size']}.json"
    split = json.loads(split_file.read_text(encoding='utf-8'))
    training, validation = split['train'], split['validation']
    if (len(training) != 45000 or len(validation) != 5000 or
        set(training) & set(validation) or len(set(training) | set(validation)) != 50000):
        raise ValueError('Invalid existing training/validation split')
    if not 1 <= samples <= len(validation):raise ValueError('Invalid validation sample count')
    dataset = TrainingPartitionOnly(str(ROOT/'data'), train=True, download=False)
    images = torch.from_numpy(dataset.data).permute(0, 3, 1, 2).contiguous()
    return images, torch.tensor(validation[:samples])
