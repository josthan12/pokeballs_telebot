# 📦 Inventory Bot — Quick Add Guide

This guide explains how to add new eras and new sets to the bot.

You only need to edit the data, callback mappings, and menu buttons below. Do NOT modify core bot logic.

---

# ➕ ADDING A NEW ERA

An era represents a full menu screen (e.g. SV, SWSH, MEGA).

### Step 1 — Create the data structure

```python
NEW_ERA = {
    "ERA_NAME": {
        "Sealed": {
            "Example Set": {
                "Item Name": 1
            }
        },
        "Singles": {},
        "Slabs": {}
    }
}
```

---

### Step 2 — Register the era

Add the following into `ERA_CALLBACKS`:

```python
"new_era_all": ("New Era Name", NEW_ERA["ERA_NAME"]["Sealed"]),
```

---

### Step 3 — Add era button in menu

Find the correct language era menu and add:

```python
InlineKeyboardButton("NEW ERA", callback_data="new_eng")
```

---

### Step 4 — Add route handler (REQUIRED ONLY FOR ERAS)

```python
@route("new_eng")
async def new_eng(update, context):
    await update.callback_query.edit_message_text(
        "Please choose a set:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Show All", callback_data="new_era_all")],
            [InlineKeyboardButton("Example Set", callback_data="example_set")]
        ])
    )
```

---

# ➕ ADDING A NEW SET

A set represents inventory inside an era.

---

### Step 1 — Add to SET_CALLBACKS

```python
"example_set": (
    "Example Set Name",
    NEW_ERA["ERA_NAME"]["Sealed"]["Example Set"]
),
```

---

### Step 2 — Add button in the era menu

Inside the correct era route menu:

```python
InlineKeyboardButton("Example Set", callback_data="example_set")
```

---

### Step 3 — Done

No other changes are required.

---

# 📌 RULES

### ✅ DO:
- Add new sets ONLY in `SET_CALLBACKS`
- Add new eras using:
  - Data dictionary
  - ERA_CALLBACKS entry
  - Menu button
  - Route handler

---

### ❌ DO NOT:
- Modify `button_handler`
- Add new if/elif logic anywhere
- Change back navigation system
- Edit formatting functions

---

# 🧠 MENTAL MODEL

- Era = menu screen → requires route
- Set = data entry → no route required
- Inventory display = automatic via existing handlers

---

# 🚀 SUMMARY TABLE

| Action | Where to edit |
|--------|--------------|
| Add new set | SET_CALLBACKS only |
| Add new era | Data + ERA_CALLBACKS + menu + route |
| Show inventory | Already handled by bot logic |
