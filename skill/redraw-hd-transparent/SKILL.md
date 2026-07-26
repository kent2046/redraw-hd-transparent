---
name: redraw-hd-transparent
description: Redraw or regenerate a reference bitmap as a clean high-resolution transparent PNG, reconstruct occluded or cropped regions, preserve important composition and style invariants, remove a chroma-key background, fit the result to an exact pixel canvas, set output PPI, and validate the alpha channel. Use when the user asks for 高清重绘、保留透明度、透明背景、去底、补全遮挡、放到指定尺寸画布、4K、300 PPI, or a high-resolution cutout derived from a supplied JPG/PNG/reference image.
---

# 高清透明重绘

Produce a visually faithful regenerated asset rather than merely sharpening the source. Preserve the user's essential composition, improve malformed details, reconstruct hidden regions when requested, and deliver a verified transparent PNG at the exact requested canvas size.

## Workflow

1. Inspect every reference image with `view_image`.
2. Record the invariants before prompting:
   - subject count and identity-neutral traits
   - composition, viewing angle, pose, and placement
   - visual style, palette, and lighting
   - objects that must remain, disappear, or be reconstructed
3. Determine the output specification. Default to the user's exact dimensions and PPI. If PPI is omitted but prior context establishes 300 PPI, use 300; otherwise use 300 for print-oriented poster assets and 72 for screen-only assets.
4. Use the built-in image generation tool. Treat the supplied image as a reference or edit target as appropriate.
5. Generate on a perfectly uniform removable chroma-key background:
   - Prefer `#00ff00` unless the subject contains important green details.
   - Prefer `#ff00ff` when green must be preserved.
   - Forbid the key color in the subject.
   - Require generous padding, crisp edges, no cast shadow, no floor, no text, and no watermark unless explicitly requested.
6. Inspect the generated result. Check subject count, anatomy, crop, style fidelity, and requested reconstruction. Iterate once with one targeted correction when a material defect remains.
7. Copy the selected generated source into the current workspace.
8. Remove the key using the installed image-generation helper:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
     --input <chroma-source.png> \
     --out <transparent-source.png> \
     --auto-key border \
     --soft-matte \
     --transparent-threshold 12 \
     --opaque-threshold 220 \
     --despill \
     --edge-contract 1
   ```

9. Run the bundled finalizer:

   ```bash
   python3 scripts/finalize_transparent.py \
     --input <transparent-source.png> \
     --output <final.png> \
     --width 3840 \
     --height 2150 \
     --dpi 300 \
     --fit contain
   ```

10. Inspect the final PNG with `view_image`. Verify exact width, height, PPI, alpha, transparent corners, clean edges, and adequate subject coverage.
11. Deliver a clickable file link, inline preview, dimensions, PPI, and confirmation that Alpha is present. Briefly summarize the final generation prompt and state that the built-in image tool was used.

## Prompt pattern

Use a compact production prompt:

```text
Use case: ads-marketing
Asset type: high-resolution transparent cutout for a <width>×<height> canvas
Input image: direct composition and style reference
Primary request: redraw the same subject at higher fidelity
Preserve: subject count, composition, angle, pose, palette, style
Improve: anatomy, edges, linework/texture, small details, resolution
Reconstruct: all requested cropped or occluded regions naturally
Composition: keep the complete subject inside frame with generous padding
Background: perfectly flat solid <key-color>, no gradient, texture, shadow, floor, or reflection
Constraints: no key color in subject; no text, logo, or watermark
Avoid: duplicate subjects, malformed anatomy, fused objects, unintended crop, style drift
```

For photorealistic food, emphasize coherent anatomy, separated claws/legs/antennae, realistic materials, and appetizing controlled highlights. For illustration, emphasize crisp outlines, clean color blocks, coherent hands/fingers, and consistent line weight.

## Output rules

- Preserve aspect ratio by default with `--fit contain`; use transparent padding to reach the exact canvas.
- Use `--fit cover` only when the user wants the asset to fill and accepts edge cropping.
- Use `--fit stretch` only when the source ratio already matches closely or the user explicitly allows distortion.
- Never overwrite the source reference.
- Keep intermediate chroma-key files under `work/` or `tmp/`; save final assets under the project's output folder.
- If chroma removal damages hair, smoke, glass, liquids, translucent edges, or reflective details, do not hide the defect. Explain that native transparency needs the image-generation CLI fallback and ask before switching models or requiring an API key.

