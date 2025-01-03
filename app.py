from flask import Flask, render_template, request, redirect, url_for, flash
from people import get_customer_by_id
from meat import meat_items

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 주문 내역을 저장할 딕셔너리 (각 customer_id에 대한 주문 내역을 저장)
orders = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        customer = get_customer_by_id(customer_id)
        if customer:
            return redirect(url_for("hand", customer_id=customer_id))
        else:
            flash("올바르지 않은 아이디입니다.")
    return render_template("index.html")

@app.route("/hand/<customer_id>", methods=["GET", "POST"])
def hand(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return redirect(url_for("index"))

    # 이미 주문한 내역이 있는지 확인
    existing_order = orders.get(customer_id)

    if request.method == "POST":
        if existing_order:
            flash("이미 주문을 완료한 고객입니다.")
            return redirect(url_for("hand", customer_id=customer_id))

        selected_items = request.form.getlist("items")
        quantities = request.form.getlist("quantities")
        order_details = []
        total_price = 0

        for item, quantity in zip(selected_items, quantities):
            quantity = int(quantity)
            meat_item = next(m for m in meat_items if m["name"] == item)
            price = meat_item["price"] * quantity
            order_details.append({"item": item, "quantity": quantity, "price": price})
            total_price += price

        orders[customer_id] = {"customer": customer, "details": order_details, "total_price": total_price}
        flash("주문이 완료되었습니다.")
        return redirect(url_for("hand", customer_id=customer_id))
    
    return render_template("hand.html", customer=customer, meat_items=meat_items, existing_order=existing_order)

@app.route("/delete_order/<customer_id>", methods=["POST"])
def delete_order(customer_id):
    if customer_id in orders:
        del orders[customer_id]
        flash("주문이 취소되었습니다.")
    return redirect(url_for("hand", customer_id=customer_id))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    admin_password = "admin123"  # 비밀번호를 하드코딩으로 설정 (보안을 위해 DB나 환경변수를 사용해야 함)
    if request.method == "POST":
        password = request.form.get("password")
        if password == admin_password:
            return redirect(url_for("hi"))
        else:
            flash("잘못된 관리자 비밀번호입니다.")
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)  # 디버깅 모드 활성화
