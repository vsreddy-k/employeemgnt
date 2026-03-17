from flask import Flask, request, jsonify
from flasgger import Swagger

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
swagger = Swagger(app)

# In-memory store: { emp_id (int) -> {"emp_id": int, "name": str, "salary": int} }
# All data is lost when the app restarts — that's intentional.
employees: dict = {}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/add", methods=["POST"])
def add_employee():
    """
    Add a new employee.
    Accepts JSON body or form data with fields: id, name, salary
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [id, name, salary]
          properties:
            id:     { type: integer }
            name:   { type: string }
            salary: { type: integer }
    responses:
      201:
        description: Employee added successfully
      400:
        description: Missing required fields
      409:
        description: Employee with that ID already exists
    """
    if request.is_json:
        data   = request.get_json()
        emp_id = data.get("id")
        name   = data.get("name")
        salary = data.get("salary")
    else:
        emp_id = request.form.get("id")
        name   = request.form.get("name")
        salary = request.form.get("salary")

    if emp_id is None or not name or salary is None:
        return jsonify({"message": "Missing required fields: id, name, salary"}), 400

    emp_id = int(emp_id)

    if emp_id in employees:
        return jsonify({"message": f"Employee with id {emp_id} already exists"}), 409

    employees[emp_id] = {"emp_id": emp_id, "name": name, "salary": int(salary)}
    return jsonify({"message": "Employee added successfully"}), 201


@app.route("/byId/<int:emp_id>", methods=["GET"])
def get_employee_by_id(emp_id):
    """
    Get employee by ID.
    ---
    parameters:
      - name: emp_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Employee found
      404:
        description: Employee not found
    """
    employee = employees.get(emp_id)
    if employee:
        return jsonify(employee)
    return jsonify({"message": "Employee not found"}), 404


@app.route("/byName/<string:name>", methods=["GET"])
def get_employee_by_name(name):
    """
    Get employee by name (case-insensitive).
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Employee found
      404:
        description: Employee not found
    """
    for emp in employees.values():
        if emp["name"].lower() == name.lower():
            return jsonify(emp)
    return jsonify({"message": "Employee not found"}), 404


@app.route("/all", methods=["GET"])
def get_all_employees():
    """
    Get all employees.
    ---
    responses:
      200:
        description: List of all employees
    """
    return jsonify(list(employees.values()))


@app.route("/update", methods=["PUT"])
def update_employee():
    """
    Update employee name and/or salary. Requires JSON body.
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [emp_id]
          properties:
            emp_id: { type: integer }
            name:   { type: string }
            salary: { type: integer }
    responses:
      200:
        description: Employee updated successfully
      400:
        description: JSON body required or emp_id missing
      404:
        description: Employee not found
    """
    if not request.is_json:
        return jsonify({"message": "Invalid content type. Please send JSON data."}), 400

    data   = request.get_json()
    emp_id = data.get("emp_id")

    if emp_id is None:
        return jsonify({"message": "emp_id is required"}), 400

    emp_id = int(emp_id)
    employee = employees.get(emp_id)

    if not employee:
        return jsonify({"message": "Employee not found"}), 404

    if "name"   in data: employee["name"]   = data["name"]
    if "salary" in data: employee["salary"] = int(data["salary"])

    return jsonify({"message": "Employee updated successfully"})


@app.route("/delete/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    """
    Delete employee by ID.
    ---
    parameters:
      - name: emp_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Employee deleted successfully
      404:
        description: Employee not found
    """
    if emp_id not in employees:
        return jsonify({"message": "Employee not found"}), 404

    del employees[emp_id]
    return jsonify({"message": "Employee deleted successfully"})


@app.route("/delete", methods=["POST"])
def delete_employee_by_form():
    """
    Delete employee via form POST (field: delete_id).
    ---
    parameters:
      - name: delete_id
        in: formData
        type: integer
        required: true
    responses:
      200:
        description: Employee deleted successfully
      400:
        description: delete_id is required
      404:
        description: Employee not found
    """
    emp_id = request.form.get("delete_id")
    if emp_id is None:
        return jsonify({"message": "delete_id is required"}), 400

    emp_id = int(emp_id)
    if emp_id not in employees:
        return jsonify({"message": "Employee not found"}), 404

    del employees[emp_id]
    return jsonify({"message": "Employee deleted successfully"})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "employee_count": len(employees)}), 200


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
