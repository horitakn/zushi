from flask import Flask, render_template, request, redirect, url_for, flash
import pickle
import math

app = Flask(__name__)
app.secret_key = "secret_key"

class MarinaTripApp:
    def __init__(self):
        # メンバリスト
        self.members = ["西村", "大阿久", "堀田"]
        
        # 割り勘割合
        self.split_ratios = {
            "西村": 30,
            "大阿久": 35,
            "堀田": 35
        }
        
        # 購入した品目のリスト
        self.items = []

    def add_purchase(self, member, amount, item):
        self.items.append((member, amount, item))
        self.save_data()

    def delete_purchase(self, item_id):
        del self.items[int(item_id) - 1]
        self.save_data()

    def calculate_split(self):
        total_amount = sum(amount for _, amount, _ in self.items)
        total_ratio = sum(self.split_ratios.values())

        if total_ratio != 100:
            flash("割合の合計が100%ではありません。", "error")
            return {}

        split_amounts = {member: total_amount * ratio / 100 for member, ratio in self.split_ratios.items()}
        paid_amounts = {member: 0 for member in self.members}

        for member, amount, _ in self.items:
            paid_amounts[member] += amount

        split_result = {member: math.ceil(paid_amounts[member] - split_amounts[member]) for member in self.members}
        return split_result

    def save_data(self):
        with open("marina_trip_data.pkl", "wb") as f:
            pickle.dump(self.items, f)

    def load_data(self):
        try:
            with open("marina_trip_data.pkl", "rb") as f:
                self.items = pickle.load(f)
        except FileNotFoundError:
            pass

marina_trip_app = MarinaTripApp()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form["action"] == "add_purchase":
            member = request.form["member"]
            amount = int(request.form["amount"])
            item = request.form["item"]
            marina_trip_app.add_purchase(member, amount, item)
        elif request.form["action"] == "delete_purchase":
            item_id = request.form["item_id"]
            marina_trip_app.delete_purchase(item_id)
        elif request.form["action"] == "change_ratio":
            for member in marina_trip_app.members:
                ratio = int(request.form[member])
                marina_trip_app.split_ratios[member] = ratio
        return redirect(url_for("index"))
    marina_trip_app.load_data()
    split_result = marina_trip_app.calculate_split()
    return render_template("index.html", members=marina_trip_app.members, items=marina_trip_app.items, split_result=split_result, split_ratios=marina_trip_app.split_ratios)

if __name__ == "__main__":
    app.run(debug=True)
