def restructure_product_creation_data(data):
    """
    Restructures request data for product creation, handling nested images and sizes correctly.
    """
    print("Request data:", data)

    product_data = {
        "name": "",
        "design_type": "",
        "description": "",
        "price": "",
        "category": "",
        "images": [],
        "sizes": [],
    }

    for key, value in data.lists():
        if key == "name":
            product_data["name"] = value[0]
        elif key == "design_type":
            product_data["design_type"] = value[0]
        elif key == "description":
            product_data["description"] = value[0]
        elif key == "price":
            product_data["price"] = value[0]
        elif key == "category":
            product_data["category"] = value[0]

        elif key.startswith("images"):
            # Extract the index and field (either 'image' or 'is_main')
            parts = key.split("[")
            image_index = int(parts[1].split("]")[0])
            image_field = parts[2][:-1]  # Remove the trailing bracket

            # Ensure the list is large enough
            while len(product_data["images"]) <= image_index:
                product_data["images"].append({"image": None, "is_main": False})

            # Assign value to the correct field
            if image_field == "image":
                product_data["images"][image_index]["image"] = (
                    value[0] if value[0] != "undefined" else None
                )
            elif image_field == "is_main":
                product_data["images"][image_index]["is_main"] = (
                    value[0].lower() == "true"
                )

        elif key.startswith("sizes"):
            # Extract the index and field (either 'size' or 'quantity')
            parts = key.split("[")
            size_index = int(parts[1].split("]")[0])
            size_field = parts[2][:-1]  # Remove the trailing bracket

            # Ensure the list is large enough
            while len(product_data["sizes"]) <= size_index:
                product_data["sizes"].append({"size": "", "quantity": 0})

            # Assign value to the correct field
            if size_field == "size":
                product_data["sizes"][size_index]["size"] = value[0]
            elif size_field == "quantity":
                product_data["sizes"][size_index]["quantity"] = int(value[0])

    return product_data
