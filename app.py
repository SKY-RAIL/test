from flask import Flask, render_template, request, redirect, url_for, flash
from people import get_customer_by_id
from meat import meat_items
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 주문 내역을 저장할 딕셔너리
orders = {}  # 직접 수령 주문
delivery_orders = {}  # 배달 수령 주문

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        customer = get_customer_by_id(customer_id)
        if customer:
            if request.form.get("order_type") == "direct":
                return redirect(url_for("hand", customer_id=customer_id))
            elif request.form.get("order_type") == "delivery":
                return redirect(url_for("car", customer_id=customer_id))
        else:
            flash("올바르지 않은 아이디입니다.")
    return render_template("index.html")

@app.route("/hand/<customer_id>", methods=["GET", "POST"])
def hand(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        flash("올바르지 않은 아이디입니다.")
        return redirect(url_for("index"))

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

@app.route("/car/<customer_id>", methods=["GET", "POST"])
def car(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        flash("올바르지 않은 아이디입니다.")
        return redirect(url_for("index"))

    existing_order = delivery_orders.get(customer_id)
    if request.method == "POST":
        if existing_order:
            flash("이미 주문을 완료한 고객입니다.")
            return redirect(url_for("car", customer_id=customer_id))

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

        delivery_orders[customer_id] = {
            "customer": customer,
            "details": order_details,
            "total_price": total_price,
            "sender_name": request.form.get("sender_name"),
            "sender_phone": request.form.get("sender_phone"),
            "sender_address": request.form.get("sender_address"),
            "receiver_name": request.form.get("receiver_name"),
            "receiver_phone": request.form.get("receiver_phone"),
            "receiver_address": request.form.get("receiver_address"),
            "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        flash("배달 주문이 완료되었습니다.")
        return redirect(url_for("car", customer_id=customer_id))

    return render_template("car.html", customer=customer, meat_items=meat_items, existing_order=existing_order)

@app.route("/delete_order/<customer_id>", methods=["POST"])
def delete_order(customer_id):
    if customer_id in orders:
        del orders[customer_id]
        flash("주문이 취소되었습니다.")
    return redirect(url_for("hand", customer_id=customer_id))

@app.route("/delete_delivery_order/<customer_id>", methods=["POST"])
def delete_delivery_order(customer_id):
    if customer_id in delivery_orders:
        del delivery_orders[customer_id]
        flash("배달 주문이 취소되었습니다.")
    return redirect(url_for("car", customer_id=customer_id))

@app.route("/admin", methods=["GET"])
def admin():
    return render_template("admin.html")

@app.route("/view_orders", methods=["GET"])
def view_orders():
    return render_template("view_orders.html", orders=orders)

@app.route("/carview", methods=["GET"])
def carview():
    return render_template("carview.html", orders=delivery_orders)

if __name__ == "__main__":
    app.run(debug=True)
