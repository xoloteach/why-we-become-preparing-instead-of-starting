# Why You Keep Preparing Instead of Starting.

Private Why We Become episode source. Canonical script and supplied artwork are preserved in the private Notion project with the same title. Original wording and artwork are retained.

## Build

The complete renderer is v2/render_motion.py, adapted from the user-approved motion-first benchmark. Source inputs are the original image ZIP and lossless final narration FLAC. No provider credentials are needed to reproduce a render.

See .github/workflows/render.yml for the full standalone dependency and build recipe. Extract the supplied ZIP, run extract_panels.py, put inputs/FSRCNN_x4.pb in /data/sr_models, decode inputs/voiceover.flac to voiceover.wav, then run prepare_art.py, build_plan.py, build_mix.py, make_thumbnail.py and the renderer. export_qa.py verifies the result and packages reproducible source and review frames.

Narration uses flux-cole-en, 0.95 speed and calm expressivity; nova-3 aligned the final processed audio. Provider secrets remain outside this repository. The raw TTS text and original caption/transcript wording are unchanged. Natural spoken contractions and short STT recognition variants are reviewed in script_alignment.json.

123 phrase-timed scenes use 87 of 88 supplied illustrations. The remaining illustrated panel and five blank grid cells have explicit omission reasons. All 88 illustrated panels have a 4× FSRCNN reconstruction and are available to reproduce the project.

## Quality gates

1920×1080 / 30 fps; duration within 0.5 seconds of final narration; -17.5 to -14.5 LUFS; audio present; nonempty word-highlighted captions. Structural headline/cue audit and representative local motion samples precede the persistent full render. Actual final frames and technical measurements must be reviewed before publishing a new versioned release.

A workflow artifact is not a release. Never overwrite an existing published version. Keep the repository private. Never commit credentials, .env files, runtime logs or unrelated private workspace exports.
