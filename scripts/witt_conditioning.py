"""Separate actual AWGN SNR from the SNR supplied to author WITT components."""
def conditioned_forward(model, images, physical_snr, encoder_snr, decoder_snr=None):
    if decoder_snr is None:
        decoder_snr = encoder_snr
    _, _, height, width = images.shape
    if height != model.H or width != model.W:
        model.encoder.update_resolution(height, width)
        model.decoder.update_resolution(height // 2**model.downsample, width // 2**model.downsample)
        model.H, model.W = height, width
    feature = model.encoder(images, encoder_snr, model.model)
    cbr = feature.numel() / 2 / images.numel()
    received = model.feature_pass_channel(feature, physical_snr) if model.pass_channel else feature
    reconstruction = model.decoder(received, decoder_snr, model.model)
    return reconstruction, cbr
