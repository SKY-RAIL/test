from flask import Flask, render_template, request, redirect, url_for, flash
from people import get_customer_by_id
from meat import meat_items

app = Flask(__name__)
app.secret_key = "your_secret_key"

orders = []

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

    # 고객이 이미 주문을 한 경우, 다시 주문할 수 없도록 제한
    existing_order = next((order for order in orders if order["customer"]["id"] == customer_id), None)
    if existing_order:
        flash("이미 주문을 완료하셨습니다.")
        return redirect(url_for("hi"))

    if request.method == "POST":
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
        
        orders.append({"customer": customer, "details": order_details, "total_price": total_price})
        return redirect(url_for("hand", customer_id=customer_id))  # 주문 후 다시 주문 페이지로 돌아가기

    return render_template("hand.html", customer=customer, meat_items=meat_items)

@app.route("/hi")
def hi():
    return render_template("hi.html", orders=orders)

@app.route("/delete_order/<int:order_index>", methods=["POST"])
def delete_order(order_index):
    if 0 <= order_index < len(orders):
        del orders[order_index]
    return redirect(url_for("hi"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # 관리자 모드 접근 처리
    admin_password = "admin123"  # 비밀번호를 하드코딩으로 설정 (보안을 위해 DB나 환경변수를 사용해야 함)
    if request.method == "POST":
        password = request.form.get("password")
        if password == admin_password:
            return redirect(url_for("hi"))
        else:
            flash("잘못된 관리자 비밀번호입니다.")
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)
