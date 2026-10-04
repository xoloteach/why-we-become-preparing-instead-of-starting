# Why You Keep Preparing Instead of Starting.

Why We Become — 16:9 motion-first episode production.

## Canonical source

Title, unchanged narration script, original contact-sheet ZIP and production checkpoint are preserved on the private Notion project:
https://www.notion.so/4b9697e4e7f54c85ae94d15c5957586b

## Current status

Source preflight complete, not a finished video. Ten source sheets were visually inspected individually. Boundary-aware extraction produced 88 illustrated native panels from 93 physical grid cells, excluding five blank cells. The source sheets are 1672×941. Sheet 04 has four rows; all others have three.

The checkpoint archive on the Notion page contains original artwork, native crops, panel_inventory.json, pending upscale_report.json, extraction source and artwork review notes. Native crops have not been individually visually approved. No neural upscaling, narration, alignment, locked scene map, master render or release is claimed.

Computer internet access must be enabled before external narration/alignment requests or downloads. No active render job exists.

## Offline reproduction

Restore stickman_contact_sheets from the original ZIP in the private Notion project. With Pillow and numpy installed, run:

```sh
python3 extract_panels.py .
```

Outputs are atomic native crops, a boundary-and-panel inventory, and a pending-upscale report. No network access or credentials are used by this extractor.

## Next production gates

1. Synthesize the original script through the validated Deepgram narration route; verify provider support before selecting parameters.
2. Complete vocal processing and pause trimming, then align word/cue timestamps against the final audio.
3. Prepare reconstructed artwork/masks and write per-panel scene/cue assignments, use/omission reasons and synchronization review.
4. Build semantic motion, captions, ducked music/SFX and canonical end card.
5. Persist source/assets before full rendering; inspect actual captioned chapter frames and motion.
6. Verify 1920×1080 at 30 fps, audio duration within 0.5 s, non-silent -17.5 to -14.5 LUFS and nonempty subtitles.
7. Create a new private versioned release only after QA, with master, thumbnail, real chapter times, transcript, source and QA report.

Keep this repository private. Never copy credentials, .env files, private workspace exports or credential-bearing logs into source or release archives.
