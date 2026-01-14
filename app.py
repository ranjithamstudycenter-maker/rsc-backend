from flask import Flask, render_template, request, redirect, session, send_from_directory
import os
import razorpay
import json

# -------------------- APP CONFIG --------------------
app = Flask(__name__)
app.secret_key = "supersecretkey123"

PDF_FOLDER = "rsc-download"
os.makedirs(PDF_FOLDER, exist_ok=True)

# -------------------- LOAD RAZORPAY KEYS --------------------
with open("admin.json") as f:
    keys = json.load(f)

razorpay_client = razorpay.Client(
    auth=(keys["razorpay_key"], keys["razorpay_secret"])
)

# -------------------- HOME --------------------
@app.route("/")
def home():
    return render_template("home.html")

# -------------------- LIST PDF DOWNLOADS --------------------
@app.route("/downloads")
def downloads():
    pdfs = os.listdir(PDF_FOLDER)
    return render_template("downloads.html", pdfs=pdfs)

# -------------------- REDIRECT TO PAYMENT --------------------
@app.route("/download/<pdf_name>")
def download(pdf_name):
    return redirect(f"/pay?file={pdf_name}")

# -------------------- PAYMENT PAGE --------------------
@app.route("/pay")
def pay():
    file = request.args.get("file")

    order = razorpay_client.order.create({
        "amount": 4900,  # ₹49
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        "pay.html",
        file=file,
        order_id=order["id"],
        razorpay_key=keys["razorpay_key"]
    )

# -------------------- PAYMENT SUCCESS --------------------
@app.route("/success", methods=["POST"])
def success():
    pdf = request.form.get("file")
    return send_from_directory(PDF_FOLDER, pdf, as_attachment=True)

# -------------------- ADMIN LOGIN --------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/upload")
    return '''
    <h2>Admin Login</h2>
    <form method="post">
        <input type="password" name="password" placeholder="Enter password" required>
        <button>Login</button>
    </form>
    '''

# -------------------- PDF UPLOAD --------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get("admin"):
        return redirect("/admin")

    if request.method == "POST":
        file = request.files["pdf"]
        if file:
            file.save(os.path.join(PDF_FOLDER, file.filename))

    return '''
    <h2>Upload Maths PDF</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="pdf" accept=".pdf" required>
        <button>Upload</button>
    </form>
    '''

# -------------------- RUN APP --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
