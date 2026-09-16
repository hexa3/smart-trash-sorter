# Demo videos

Place the 2–4 final demo clips in this folder using these names:

- `01-overview.mp4` — full system demonstration
- `02-recyclable-bottle.mp4` — recyclable item sorting
- `03-trash-food.mp4` — trash item sorting
- `04-mechanism-closeup.mp4` — optional mechanism detail

Video files are ignored by default because they are often too large for normal
Git repositories. Choose one of these publishing approaches:

1. Upload the clip to YouTube/Drive and add its public link to the main README.
2. If each clip is under 100 MB, remove its matching ignore rule and commit it.
3. For larger files, use Git LFS:

   ```bash
   git lfs install
   git lfs track "videos/*.mp4"
   git add .gitattributes videos/*.mp4
   ```

For consistent results, export in H.264 MP4 at 1080p or 720p and trim the clips
to the key action.
