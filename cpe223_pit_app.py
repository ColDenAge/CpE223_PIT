import streamlit as st
import math
import re
import pandas as pd

# --- Expression Fixing ---
def fix_expression(expr):
    expr = expr.replace('+', ' + ')
    expr = expr.replace('-', ' - ')
    expr = expr.replace('*', ' * ')
    expr = expr.replace('/', ' / ')
    expr = expr.replace('^', '**')
    expr = re.sub(r'\*\*(\d+)([a-zA-Z])', r'**\1*\2', expr)
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
    expr = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr)
    expr = expr.replace('s*in', 'sin').replace('c*os', 'cos')
    expr = expr.replace('t*an', 'tan').replace('e*xp', 'exp')
    expr = expr.replace('l*og', 'log').replace('s*qrt', 'sqrt')
    expr = re.sub(r'\)([a-zA-Z0-9])', r')*\1', expr)
    return ' '.join(expr.split())

def make_user_function(expr):
    expr = fix_expression(expr)
    def func(x, y):
        return eval(expr, {"__builtins__": None, "x": x, "y": y, "math": math,
                           "sin": math.sin, "cos": math.cos, "tan": math.tan,
                           "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
                           "pi": math.pi, "e": math.e})
    return func

# --- Adams-Bashforth Method ---
def adams_bashforth_2(f, x0, y0, h, n):
    x = [x0]
    y = [y0]
    y1 = y0 + h * f(x0, y0)
    x.append(x0 + h)
    y.append(y1)

    for i in range(1, n):
        xi, yi = x[i], y[i]
        xi_1, yi_1 = x[i - 1], y[i - 1]
        x_next = xi + h
        y_next = yi + h * (3 * f(xi, yi) - f(xi_1, yi_1)) / 2
        x.append(x_next)
        y.append(y_next)

    return x, y

# --- Streamlit Interface ---
st.title("Adams-Bashforth 2-Step Method Calculator")

st.markdown("""
Enter a differential equation in terms of `x` and `y`, like:
- `2x^2 + 4y`
- `3xy + sin(x)`
- `e^x - y`

Operators supported: `^`, `sin()`, `cos()`, `exp()`, `log()`, etc.
Multiplication like `2x` is automatically fixed to `2*x`.
""")

expr = st.text_input("f(x, y) =", "x + y")
x0 = st.number_input("Initial x₀", value=0.0)
y0 = st.number_input("Initial y₀", value=1.0)
h = st.number_input("Step size h", value=0.1)
n = st.number_input("Number of steps n", min_value=1, step=1, value=10)

if st.button("Calculate"):
    try:
        f = make_user_function(expr)
        xs, ys = adams_bashforth_2(f, x0, y0, h, n)
        df = pd.DataFrame({"Step": range(len(xs)), "x": xs, "y": ys})
        st.success("Calculation successful!")
        st.dataframe(df.style.format({"x": "{:.4f}", "y": "{:.4f}"}))
    except Exception as e:
        st.error(f"Error: {e}")