import sqlite3
import os
import math


# =====================================================
# DATABASE CONFIGURATION
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FOLDER = os.path.join(BASE_DIR, "database")
os.makedirs(DB_FOLDER, exist_ok=True)

DB_NAME = os.path.join(DB_FOLDER, "disaster.db")


def connect_db():
    return sqlite3.connect(DB_NAME)


# =====================================================
# INCIDENT TABLE
# =====================================================

def create_table():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disaster TEXT,
            location TEXT,
            affected_people INTEGER,
            severity TEXT,
            description TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_incident(disaster, location, affected_people,
                 severity, description, status="Active"):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO incidents
        (disaster, location, affected_people,
         severity, description, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        disaster,
        location,
        affected_people,
        severity,
        description,
        status
    ))

    conn.commit()
    conn.close()


def get_incidents():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, disaster, location, affected_people,
               severity, description, status
        FROM incidents
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return records


def delete_incident(incident_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM incidents WHERE id = ?",
        (incident_id,)
    )

    conn.commit()
    conn.close()


# =====================================================
# RESOURCE TABLE
# =====================================================

def create_resource_table():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_name TEXT,
            category TEXT,
            quantity INTEGER,
            location TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_resource(resource_name, category,
                 quantity, location, status="Available"):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resources
        (resource_name, category, quantity, location, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        resource_name,
        category,
        quantity,
        location,
        status
    ))

    conn.commit()
    conn.close()


def get_resources():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, resource_name, category,
               quantity, location, status
        FROM resources
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return records


def delete_resource(resource_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM allocations
        WHERE resource_id = ? AND status = 'Allocated'
    """, (resource_id,))

    active = cursor.fetchone()[0]

    if active > 0:
        conn.close()
        return False, "Resource has active allocations."

    cursor.execute(
        "DELETE FROM resources WHERE id = ?",
        (resource_id,)
    )

    conn.commit()
    conn.close()

    return True, "Resource deleted successfully."


# =====================================================
# ALLOCATION TABLE
# =====================================================

def create_allocation_table():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            resource_id INTEGER,
            resource_name TEXT,
            quantity INTEGER,
            allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Allocated'
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
# MANUAL RESOURCE ALLOCATION
# =====================================================

def allocate_resource(incident_id, resource_id, quantity):

    conn = connect_db()

    try:

        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT resource_name, quantity
            FROM resources
            WHERE id = ?
        """, (resource_id,))

        resource = cursor.fetchone()

        if resource is None:
            conn.rollback()
            return False, "Resource not found."

        resource_name, available_quantity = resource

        if quantity <= 0:
            conn.rollback()
            return False, "Quantity must be greater than zero."

        if available_quantity < quantity:
            conn.rollback()
            return False, "Insufficient resource quantity."

        cursor.execute("""
            UPDATE resources
            SET quantity = quantity - ?
            WHERE id = ?
        """, (quantity, resource_id))

        cursor.execute("""
            UPDATE resources
            SET status = CASE
                WHEN quantity <= 0 THEN 'Unavailable'
                ELSE 'Available'
            END
            WHERE id = ?
        """, (resource_id,))

        cursor.execute("""
            INSERT INTO allocations
            (incident_id, resource_id, resource_name, quantity, status)
            VALUES (?, ?, ?, ?, 'Allocated')
        """, (
            incident_id,
            resource_id,
            resource_name,
            quantity
        ))

        conn.commit()

        return True, "Resource allocated successfully!"

    except Exception as error:

        conn.rollback()
        return False, str(error)

    finally:

        conn.close()


# =====================================================
# AUTOMATIC RESOURCE ALLOCATION
# =====================================================

def auto_allocate_resources(incident_id, recommended_resources):

    conn = connect_db()

    try:

        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        # Get incident details

        cursor.execute("""
            SELECT disaster, location, affected_people, severity
            FROM incidents
            WHERE id = ?
        """, (incident_id,))

        incident = cursor.fetchone()

        if incident is None:
            conn.rollback()
            return False, "Incident not found.", [], []

        disaster, location, people, severity = incident

        people = max(1, int(people or 1))

        # Prevent duplicate active allocation

        cursor.execute("""
            SELECT COUNT(*)
            FROM allocations
            WHERE incident_id = ?
            AND status = 'Allocated'
        """, (incident_id,))

        if cursor.fetchone()[0] > 0:
            conn.rollback()

            return (
                False,
                "This incident already has active allocations. "
                "Release them before allocating again.",
                [],
                []
            )

        # Map recommendations to inventory categories

        category_mapping = {
            "Ambulances": "Ambulance",
            "Additional Ambulances": "Ambulance",
            "Ambulance": "Ambulance",

            "Rescue Teams": "Rescue Team",
            "Rescue Team": "Rescue Team",
            "Firefighters": "Rescue Team",
            "Emergency Response Team": "Rescue Team",
            "Rescue Support Team": "Rescue Team",

            "Food Supplies": "Food Supplies",

            "Drinking Water": "Water Supplies",
            "Water Supplies": "Water Supplies",

            "Medical Kits": "Medical Supplies",
            "Additional Medical Kits": "Medical Supplies",
            "Medical Supplies": "Medical Supplies",

            "Rescue Boats": "Rescue Boats",

            "Fire Engines": "Fire Engines",

            "Emergency Shelters": "Emergency Shelters",
            "Emergency Shelter": "Emergency Shelters",
            "Temporary Shelters": "Emergency Shelters",

            "Excavators": "Heavy Equipment",
            "Heavy Equipment": "Heavy Equipment"
        }

        # Calculate required quantities

        def required_quantity(category):

            if category in ["Ambulance", "Rescue Team",
                            "Rescue Boats", "Fire Engines"]:
                return max(1, math.ceil(people / 50))

            if category in ["Food Supplies", "Water Supplies"]:
                return people

            if category == "Medical Supplies":
                return max(1, math.ceil(people / 10))

            if category == "Emergency Shelters":
                return max(1, math.ceil(people / 20))

            if category == "Heavy Equipment":
                return max(1, math.ceil(people / 100))

            return 1

        allocated_records = []
        unavailable = []

        # Process each recommended category

        categories = list(dict.fromkeys(
            category_mapping[item]
            for item in recommended_resources
            if item in category_mapping
        ))

        for category in categories:

            required = required_quantity(category)
            remaining = required
            total_allocated = 0

            # Same district first, then other locations

            cursor.execute("""
                SELECT id, resource_name, quantity, location
                FROM resources
                WHERE category = ?
                AND quantity > 0
                ORDER BY
                    CASE
                        WHEN LOWER(TRIM(location)) =
                             LOWER(TRIM(?))
                        THEN 0
                        ELSE 1
                    END,
                    quantity DESC,
                    id ASC
            """, (category, location))

            available_resources = cursor.fetchall()

            for resource in available_resources:

                if remaining <= 0:
                    break

                resource_id = resource[0]
                resource_name = resource[1]
                stock = resource[2]
                resource_location = resource[3]

                quantity_to_allocate = min(stock, remaining)

                # Reduce inventory

                cursor.execute("""
                    UPDATE resources
                    SET quantity = quantity - ?,
                        status = CASE
                            WHEN quantity - ? <= 0
                            THEN 'Unavailable'
                            ELSE 'Available'
                        END
                    WHERE id = ?
                """, (
                    quantity_to_allocate,
                    quantity_to_allocate,
                    resource_id
                ))

                # Save allocation history

                cursor.execute("""
                    INSERT INTO allocations
                    (incident_id, resource_id, resource_name,
                     quantity, status)
                    VALUES (?, ?, ?, ?, 'Allocated')
                """, (
                    incident_id,
                    resource_id,
                    resource_name,
                    quantity_to_allocate
                ))

                allocated_records.append({
                    "Resource": resource_name,
                    "Category": category,
                    "Quantity": quantity_to_allocate,
                    "Location": resource_location
                })

                remaining -= quantity_to_allocate
                total_allocated += quantity_to_allocate

            # Record shortages

            if remaining > 0:

                unavailable.append({
                    "Category": category,
                    "Required": required,
                    "Allocated": total_allocated,
                    "Shortage": remaining
                })

        conn.commit()

        message = "Automatic allocation completed successfully!"

        if not allocated_records:
            message = "No matching resources were available."

        return True, message, allocated_records, unavailable

    except Exception as error:

        conn.rollback()

        return False, str(error), [], []

    finally:

        conn.close()


# =====================================================
# GET ALLOCATION HISTORY
# =====================================================

def get_allocations(incident_id=None):

    conn = connect_db()
    cursor = conn.cursor()

    if incident_id is not None:

        cursor.execute("""
            SELECT id, incident_id, resource_id,
                   resource_name, quantity,
                   allocated_at, status
            FROM allocations
            WHERE incident_id = ?
            ORDER BY id DESC
        """, (incident_id,))

    else:

        cursor.execute("""
            SELECT id, incident_id, resource_id,
                   resource_name, quantity,
                   allocated_at, status
            FROM allocations
            ORDER BY id DESC
        """)

    records = cursor.fetchall()
    conn.close()

    return records


# =====================================================
# RELEASE ALLOCATED RESOURCE
# =====================================================

def release_resource(allocation_id):

    conn = connect_db()

    try:

        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT resource_id, quantity, status
            FROM allocations
            WHERE id = ?
        """, (allocation_id,))

        allocation = cursor.fetchone()

        if allocation is None:
            conn.rollback()
            return False, "Allocation not found."

        resource_id, quantity, status = allocation

        if status == "Released":
            conn.rollback()
            return False, "This allocation has already been released."

        # Restore inventory

        cursor.execute("""
            UPDATE resources
            SET quantity = quantity + ?,
                status = 'Available'
            WHERE id = ?
        """, (quantity, resource_id))

        # Update allocation status

        cursor.execute("""
            UPDATE allocations
            SET status = 'Released'
            WHERE id = ?
        """, (allocation_id,))

        conn.commit()

        return True, "Resource released successfully!"

    except Exception as error:

        conn.rollback()
        return False, str(error)

    finally:

        conn.close()