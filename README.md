# Star Soccer Rebooted packs

This repository is the index of the data packs of
[Star Soccer Rebooted](https://github.com/Stiven-Gjekaj/StarSoccerRebooted).
The pack browser of the app reads `index.txt`, downloads a pack, checks
its SHA-256, and installs it.

## The index

`index.txt` has one row for each pack. The cells are separated by a tab.
The first row has the names of the columns.

| Column | Value |
| --- | --- |
| `id` | The id in `pack.txt`: 1 to 47 small letters, digits, `-`, and `_` |
| `name` | The name that the app shows |
| `author` | The author of the pack |
| `version` | The version in `pack.txt` |
| `format` | The format in `pack.txt`. The app reads format 1. |
| `size` | The size of the zip file in bytes |
| `sha256` | The SHA-256 of the zip file, in small hex digits |
| `url` | The `https://` address of the zip file |

The format of a pack is in
[docs/packs.md](https://github.com/Stiven-Gjekaj/StarSoccerRebooted/blob/main/docs/packs.md)
of the game.

## Add a pack

1. Make the zip file of the pack. The script `tools/make_pack.sh` of the
   game makes it.
2. Put the zip file on a server that has `https://`, for example as the
   file of a GitHub release.
3. Get the size and the SHA-256 of the zip file:

       wc -c < my-pack.zip
       shasum -a 256 my-pack.zip

4. Add one row to `index.txt`, and open a pull request.

The check of each pull request downloads each pack and refuses the pull
request when:

- an id is not correct, or is there two times;
- the size or the SHA-256 is not the size or the SHA-256 of the download;
- `pack.txt` of the zip file has another id, version, or format;
- the zip file has a file that is not data (only `.txt`, `.png`, `.jpg`,
  `.uis`, `.uih`, and `.patch`), a file of more than 16 MB, or a name
  that goes out of the pack.

Run the check before you open the pull request:

    python3 tools/check_index.py index.txt

## The rules of a pack

- A pack holds only data. It holds no code.
- Put only images that you have the right to share.
