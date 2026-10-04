# Why You Keep Preparing Instead of Starting.

Why We Become — 16:9 motion-first episode production. This repository remains private.

## Canonical source

The private Notion project titled **Why You Keep Preparing Instead of Starting. — Why We Become** preserves the original title, unchanged narration script, supplied image ZIP and downloadable production checkpoint. Notion is the source of truth for script wording; do not copy credentials or unrelated workspace exports into this repository.

## Completed preflight

- Ten PNG sheets, each 1672×941, visually inspected individually.
- Actual grid boundaries detected rather than assumed equal thirds.
- 93 physical cells: 88 illustrated native panels and five omitted blank cells.
- Sheet 02 blanks: R1C3 and R2C2. Sheet 04 has four rows; R1C3, R2C3 and R3C3 are blank. The other sheets have three rows.
- Native crops decoded and inventoried. Individual visual crop approval and neural reconstruction remain pending.
- Checkpoint archive saved to the Notion project: original artwork, native crops, panel inventory, extraction source, pending upscale report and artwork intake review.

## Offline reproduction

Restore the stickman_contact_sheets folder from the original ZIP in Notion. With Pillow and numpy installed, run `python3 extract_panels.py .`.

The extractor uses no network or credentials. It writes native crops atomically, panel_inventory.json and a pending upscale_report.json. Do not treat its output as final visually approved artwork.

## Current blocker

Computer internet access is disabled. Narration synthesis and alignment have not been attempted. There is no voiceover, locked timing map, active render job, finished video or release from this production checkpoint.

## Next production gates

1. Verify provider support and synthesize the original script with the validated Deepgram narration route.
2. Finish vocal processing and pause trimming, then align spoken words and cue phrases against the final audio.
3. Reconstruct artwork when needed, prepare masks and write panel-by-panel scene/cue assignments, reuse and omission reasons.
4. Build semantic motion, steady highlighted captions, ducked music/SFX and canonical end card. Do not distribute panels evenly across an estimated duration.
5. Persist source/assets before full rendering, then inspect real captioned frames and motion samples.
6. Verify 1920×1080 at 30 fps; master duration within 0.5 s of audio; non-silent audio at -17.5 to -14.5 LUFS; nonempty subtitles; no material text/mask/timing defects.
7. Publish a new private versioned release only after QA, with master, thumbnail, real chapter times, transcript, source and QA report. Preserve prior releases.

Never commit keys, .env files, credential-bearing logs or private workspace exports. Use protected environment values for provider requests.
