"""
Fake banking transfer route.

EDUCATIONAL NOTE:
  The POST body contains: recipient, account_number, amount, note.
  Over HTTP all these fields are visible in plaintext.
  In Wireshark: tcp.port == 5000 && http.request.method == "POST"
  then follow the TCP stream to read the full form body.

  This demonstrates the risk of using online banking over unencrypted
  HTTP connections (e.g., public WiFi hotspots).
"""

from flask import Blueprint, render_template, request

from app.schemas import BankTransfer

banking_bp = Blueprint("banking", __name__, url_prefix="/banking")


@banking_bp.route("/", methods=["GET", "POST"])
def transfer() -> str:
    """Render the banking transfer form and handle submissions.

    GET  — Show the blank transfer form.
    POST — Echo the transfer details as a "confirmation."

    Returns:
        Rendered HTML string.
    """
    result: BankTransfer | None = None
    error: str | None = None

    if request.method == "POST":
        try:
            result = BankTransfer(
                recipient=request.form.get("recipient", "").strip(),
                amount=float(request.form.get("amount", 0)),
                note=request.form.get("note", "").strip(),
                account_number=request.form.get(
                    "account_number", ""
                ).strip(),
            )
        except Exception:
            error = "Please fill in all required fields correctly."

    return render_template("banking.html", result=result, error=error)
