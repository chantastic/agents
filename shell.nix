{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "agents-workspace";

  buildInputs = with pkgs; [
    python311
    uv
    ffmpeg
    yt-dlp
    jq
  ];

  shellHook = ''
    echo "Agents workspace dev shell"
    echo "- Python services use uv inline script metadata"
    echo "- System tools available: ffmpeg, ffprobe, yt-dlp, jq"
  '';
}
