import streamlit as st
import random
import matplotlib.pyplot as plt
import io

#############################
# Funciones para la SOPA DE LETRAS (16x16)
#############################
def generate_word_search(words, size=16):
    # Inicializa la grid y la matriz de resaltado
    grid = [['' for _ in range(size)] for _ in range(size)]
    highlight = [[False for _ in range(size)] for _ in range(size)]
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    
    for word in words:
        word = word.upper()
        placed = False
        attempts = 0
        while not placed and attempts < 500:
            attempts += 1
            r = random.randint(0, size - 1)
            c = random.randint(0, size - 1)
            dr, dc = random.choice(directions)
            if 0 <= r + dr*(len(word)-1) < size and 0 <= c + dc*(len(word)-1) < size:
                valid = True
                for i in range(len(word)):
                    cell = grid[r + dr*i][c + dc*i]
                    if cell not in ('', word[i]):
                        valid = False
                        break
                if valid:
                    for i in range(len(word)):
                        grid[r + dr*i][c + dc*i] = word[i]
                        highlight[r + dr*i][c + dc*i] = True
                    placed = True
        # Si no se puede colocar, se omite la palabra
    # Rellenar celdas vacías con letras aleatorias
    for i in range(size):
        for j in range(size):
            if grid[i][j] == '':
                grid[i][j] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return grid, highlight

#############################
# Funciones para el CRUCIGRAMA (16x16)
#############################
def can_place_word(word, row, col, orient, grid):
    size = len(grid)
    L = len(word)
    if orient == 'H':
        if col < 0 or col + L > size or row < 0 or row >= size:
            return False
        for i in range(L):
            cell = grid[row][col+i]
            if cell != ' ' and cell != word[i]:
                return False
        return True
    elif orient == 'V':
        if row < 0 or row + L > size or col < 0 or col >= size:
            return False
        for i in range(L):
            cell = grid[row+i][col]
            if cell != ' ' and cell != word[i]:
                return False
        return True
    return False

def place_word(word, row, col, orient, grid):
    positions = []
    if orient == 'H':
        for i, letter in enumerate(word):
            grid[row][col+i] = letter
            positions.append((row, col+i))
    elif orient == 'V':
        for i, letter in enumerate(word):
            grid[row+i][col] = letter
            positions.append((row+i, col))
    return positions

def generate_crossword_dynamic(words, grid_size=16):
    """
    Algoritmo mejorado:
      1. Se ordenan las palabras (sin espacios) de mayor a menor.
      2. La primera se coloca horizontal en el centro.
      3. Para cada palabra nueva se recorre el conjunto de palabras ya colocadas (en orden aleatorio)
         y se prueban todas las intersecciones posibles. Se asigna un bonus si la intersección se da en
         los extremos (inicio o fin) de la palabra candidata o de la palabra ya colocada.
      4. Se elige la colocación con mayor puntaje.
      5. Si no se encuentra ninguna intersección (es decir, la palabra no se conecta con ninguna ya colocada),
         se omite esa palabra (asegurando que el crucigrama esté completamente interconectado).
      Nota: Las celdas vacías se dejan en blanco.
    """
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    placements = []  # Cada elemento: (word, row, col, orient, positions)
    
    # Ordenar las palabras por longitud (sin espacios) de mayor a menor.
    sorted_words = sorted([w.replace(" ", "").upper() for w in words], key=len, reverse=True)
    
    # Colocar la primera palabra horizontalmente en el centro.
    first = sorted_words[0]
    row0 = grid_size // 2
    col0 = (grid_size - len(first)) // 2
    if not can_place_word(first, row0, col0, 'H', grid):
        for r in range(grid_size):
            for c in range(grid_size - len(first) + 1):
                if can_place_word(first, r, c, 'H', grid):
                    row0, col0 = r, c
                    break
            else:
                continue
            break
    pos = place_word(first, row0, col0, 'H', grid)
    placements.append((first, row0, col0, 'H', pos))
    
    # Para cada palabra restante:
    for word in sorted_words[1:]:
        best_score = -1
        best_placement = None
        # Recorre las palabras ya colocadas en orden aleatorio para no favorecer siempre la misma base.
        current_placements = placements.copy()
        random.shuffle(current_placements)
        for placed_word, pr, pc, porient, ppos in current_placements:
            for i, char_placed in enumerate(placed_word):
                for j, char_candidate in enumerate(word):
                    if char_placed == char_candidate:
                        # Si la palabra colocada es horizontal, se intenta colocar la candidata vertical, y viceversa.
                        if porient == 'H':
                            candidate_orient = 'V'
                            candidate_row = pr - j
                            candidate_col = pc + i
                        else:
                            candidate_orient = 'H'
                            candidate_row = pr + i
                            candidate_col = pc - j
                        if can_place_word(word, candidate_row, candidate_col, candidate_orient, grid):
                            # Calcular puntaje: bonus si la intersección ocurre en extremos.
                            bonus = 0
                            if j == 0 or j == len(word)-1:
                                bonus += 2
                            else:
                                bonus += 1
                            if i == 0 or i == len(placed_word)-1:
                                bonus += 1
                            score = bonus
                            # Además, sumar 1 por cada letra ya existente en la posición propuesta.
                            for k in range(len(word)):
                                r_check = candidate_row + (k if candidate_orient == 'V' else 0)
                                c_check = candidate_col + (k if candidate_orient == 'H' else 0)
                                if grid[r_check][c_check] != ' ':
                                    score += 1
                            if score > best_score:
                                best_score = score
                                best_placement = (candidate_row, candidate_col, candidate_orient)
        if best_placement:
            r, c, orient = best_placement
            pos = place_word(word, r, c, orient, grid)
            placements.append((word, r, c, orient, pos))
        else:
            # Si no se encontró intersección, se omite la palabra para garantizar la interconexión.
            st.write(f"La palabra '{word}' no se pudo conectar y fue omitida.")
    return grid, placements

#############################
# Función para convertir una grid en imagen con Matplotlib
#############################
def grid_to_image(grid, highlight=None):
    size = len(grid)
    fig, ax = plt.subplots(figsize=(size/2, size/2))
    ax.axis('off')
    table = ax.table(cellText=grid, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    
    for key, cell in table.get_celld().items():
        cell.set_height(1/size)
        cell.set_width(1/size)
        i, j = key
        if highlight is not None:
            # Para la sopa de letras: si highlight[i][j] es True, fondo amarillo; de lo contrario, fondo blanco.
            if highlight[i][j]:
                cell.set_facecolor("yellow")
            else:
                cell.set_facecolor("white")
        else:
            # Para el crucigrama: si la celda está en blanco, se pinta de plomo (#B0B0B0); si tiene letra, se deja blanca.
            if grid[i][j] == ' ':
                cell.set_facecolor("#B0B0B0")
            else:
                cell.set_facecolor("white")
    
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

#############################
# INTERFAZ CON STREAMLIT
#############################
st.title("Generador Dinámico de Crucigrama y Sopa de Letras (16x16)")

titulo = st.text_input("Título (Opcional):")

st.write("Ingresa hasta 8 palabras (una por campo):")
input_words = []
for i in range(1, 9):
    word = st.text_input(f"Palabra {i}:", key=f"word_{i}")
    if word.strip():
        input_words.append(word.strip())

if st.button("Generar Puzzles") and input_words:
    # --- SOPA DE LETRAS ---
    ws_grid, ws_highlight = generate_word_search(input_words, size=16)
    ws_buf_no_hl = grid_to_image(ws_grid, highlight=None)
    ws_buf_hl = grid_to_image(ws_grid, highlight=ws_highlight)
    
    st.subheader("Sopa de Letras (16x16)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Sin Resaltado:**")
        st.image(ws_buf_no_hl, caption="Sopa de Letras", use_container_width=True)
        st.download_button("Descargar Sin Resaltado (PNG)", data=ws_buf_no_hl, file_name="sopa_sin_resaltado.png", mime="image/png")
    with col2:
        st.markdown("**Con Resaltado:**")
        st.image(ws_buf_hl, caption="Sopa de Letras con Resaltado", use_container_width=True)
        st.download_button("Descargar Con Resaltado (PNG)", data=ws_buf_hl, file_name="sopa_con_resaltado.png", mime="image/png")
    
    # --- CRUCIGRAMA DINÁMICO ---
    cw_grid, cw_placements = generate_crossword_dynamic(input_words, grid_size=16)
    cw_buf = grid_to_image(cw_grid)
    
    st.subheader("Crucigrama (16x16)")
    st.image(cw_buf, caption="Crucigrama", use_container_width=True)
    st.download_button("Descargar Crucigrama (PNG)", data=cw_buf, file_name="crucigrama.png", mime="image/png")
    
    st.subheader("Detalle de Palabras en el Crucigrama:")
    info = ""
    for word, r, c, orient, _ in cw_placements:
        orient_str = "Horizontal" if orient == 'H' else "Vertical"
        info += f"{word}: fila {r+1}, col {c+1} ({orient_str})\n"
    st.text(info)
