"""
File upload demo route.

EDUCATIONAL NOTE:
  Files uploaded over HTTP travel as multipart/form-data in plaintext.
  Wireshark can reassemble the full file content from the TCP stream.
  Over HTTPS the same upload is opaque to any observer.

SAFETY:
  Files are read into memory (BytesIO) and immediately discarded.
  They are NEVER written to disk and NEVER executed.
  The only information retained is filename, size, and MIME type.
"""

import io

from flask import Blueprint, render_template, request

from app.schemas import UploadResult

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")

# Maximum allowed upload size for the demo: 16 MB
MAX_UPLOAD_BYTES = 16 * 1024 * 1024


@upload_bp.route("/", methods=["GET", "POST"])
def upload_file() -> str:
    """Handle the file upload form.

    GET  — Render the upload form.
    POST — Inspect the uploaded file metadata and discard content.

    Returns:
        Rendered HTML string.
    """
    result: UploadResult | None = None
    error: str | None = None

    if request.method == "POST":
        file = request.files.get("file")

        if file is None or file.filename == "":
            error = "No file selected."
        else:
            try:
                # Read into an in-memory buffer — never touch the filesystem
                buffer = io.BytesIO()
                file.save(buffer)
                size = buffer.tell()

                if size > MAX_UPLOAD_BYTES:
                    error = "File exceeds the 16 MB demo limit."
                else:
                    mime = (
                        file.content_type or "application/octet-stream"
                    )
                    result = UploadResult(
                        filename=file.filename or "unknown",
                        size_bytes=size,
                        mime_type=mime,
                    )
            except Exception as exc:
                error = f"Upload error: {exc}"

    return render_template("upload.html", result=result, error=error)
