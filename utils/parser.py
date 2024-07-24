def parser(model):
    x_s, y_s, z_s = list(), list(), list()
    for v in model.getVars():
        if v.X > 0:
            if "x" in v.varName:
                left, right = v.varName.index("["), v.varName.index("]")
                num1, num2 = v.varName[left + 1:right].split(",")
                x_s.append((int(num1), int(num2)))
            elif "y" in v.varName:
                left, right = v.varName.index("["), v.varName.index("]")
                num1, num2, num3 = v.varName[left + 1:right].split(",")
                y_s.append((int(num1), int(num2), int(num3)))
            else:
                left, right = v.varName.index("["), v.varName.index("]")
                num1, num2 = v.varName[left + 1:right].split(",")
                z_s.append((int(num1), int(num2)))
    return x_s, y_s, z_s
