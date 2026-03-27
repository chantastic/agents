{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "get-broll-assets-env";

  buildInputs = [
    # Python with spaCy for entity extraction
    (pkgs.python312.withPackages (ps: [
      ps.spacy
    ]))

    # Media processing and downloads
    pkgs.ffmpeg              # Video/audio processing
    pkgs.yt-dlp              # YouTube video downloads
    pkgs.wget                # File downloads (logos, images)

    # Browser automation
    pkgs.bun                 # JavaScript runtime (faster than Node.js)
    pkgs.playwright-driver.browsers  # Playwright browsers

    # Utilities
    pkgs.jq                  # JSON processing and querying
    pkgs.libxml2             # Provides xmllint for FCPXML validation
    pkgs.coreutils           # Unix utilities (mkdir, etc.)
  ];

  shellHook = ''
    echo "🎬 B-Roll Research Development Environment"
    echo "=========================================="
    echo ""

    # Set up spaCy model directory in user space
    export SPACY_MODEL_DIR="$HOME/.spacy/data"
    mkdir -p "$SPACY_MODEL_DIR"

    # Check if spaCy model exists
    MODEL_PATH="$SPACY_MODEL_DIR/en_core_web_sm-3.8.0"
    if [ -d "$MODEL_PATH" ]; then
      echo "✓ spaCy model ready"
    else
      echo "📦 spaCy model 'en_core_web_sm' not found"
      echo ""
      echo "   To download (one-time setup):"
      echo "   cd ~/.spacy/data"
      echo "   wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz"
      echo "   tar -xzf en_core_web_sm-3.8.0.tar.gz"
      echo ""
    fi

    echo ""
    echo "📦 Available tools:"
    echo "  python3  - Python 3.12 with spaCy NER"
    echo "  yt-dlp   - YouTube video downloader"
    echo "  ffmpeg   - Video/audio processing"
    echo "  bun      - JavaScript runtime (Playwright)"
    echo "  wget     - File downloader"
    echo "  jq       - JSON processor"
    echo "  xmllint  - XML validator (FCPXML)"
    echo ""
    echo "🚀 Ready to research b-roll assets!"
    echo ""

    # Set Playwright browser path to user cache
    export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright"
  '';
}
