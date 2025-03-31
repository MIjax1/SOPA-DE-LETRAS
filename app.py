import streamlit as st
import random
import matplotlib.pyplot as plt
import io

#############################
# Funciones para la SOPA DE LETRAS
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
    # Rellenar celdas vacías con letras aleatorias en la sopa de letras
    for i in range(size):
        for j in range(size):
            if grid[i][j] == '':
                grid[i][j] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return grid, highlight

#############################
# Funciones para el CRUCIGRAMA
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

def generate_crossword(words, grid_size=20):
    """
    Algoritmo simplificado:
      1. Coloca la primera palabra horizontal en el centro.
      2. Para cada palabra siguiente, intenta intersecar con alguna ya colocada:
         - Se recorre cada letra de la palabra candidata y de las palabras ya colocadas.
         - Si hay coincidencia, se intenta colocar la candidata en sentido perpendicular.
      3. Si no se logra intersecar, se coloca en la primera fila donde quepa horizontalmente.
    Nota: Las celdas vacías se dejan en blanco.
    """
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    placements = []  # Cada elemento: (word, row, col, orient)
    
    # Colocar la primera palabra horizontal en el centro.
    first = words[0].replace(" ", "").upper()
    row0 = grid_size // 2
    col0 = (grid_size - len(first)) // 2
    if not can_place_word(first, row0, col0, 'H', grid):
        found = False
        for r in range(grid_size):
            for c in range(grid_size - len(first) + 1):
                if can_place_word(first, r, c, 'H', grid):
                    row0, col0 = r, c
                    found = True
                    break
            if found:
                break
    place_word(first, row0, col0, 'H', grid)
    placements.append((first, row0, col0, 'H'))
    
    # Para cada palabra restante:
    for word in words[1:]:
        candidate = word.replace(" ", "").upper()
        placed = False
        for placed_word, pr, pc, porient in placements:
            for i, letter in enumerate(placed_word):
                for j, cl in enumerate(candidate):
                    if letter == cl:
                        if porient == 'H':
                            candidate_row = pr - j
                            candidate_col = pc + i
                            new_orient = 'V'
                        else:
                            candidate_row = pr + i
                            candidate_col = pc - j
                            new_orient = 'H'
                        if can_place_word(candidate, candidate_row, candidate_col, new_orient, grid):
                            place_word(candidate, candidate_row, candidate_col, new_orient, grid)
                            placements.append((candidate, candidate_row, candidate_col, new_orient))
                            placed = True
                            break
                if placed:
                    break
            if placed:
                break
        if not placed:
            # Colocar en la primera fila en la que quepa horizontalmente.
            for r in range(grid_size):
                for c in range(grid_size - len(candidate) + 1):
                    if can_place_word(candidate, r, c, 'H', grid):
                        place_word(candidate, r, c, 'H', grid)
                        placements.append((candidate, r, c, 'H'))
                        placed = True
                        break
                if placed:
                    break
    # No se rellenan celdas vacías para el crucigrama; se dejan en blanco.
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
            # Para la sopa de letras: si highlight[i][j] es True, fondo amarillo; de lo contrario blanco.
            if highlight[i][j]:
                cell.set_facecolor("yellow")
            else:
                cell.set_facecolor("white")
        else:
            # Para el crucigrama: si la celda está en blanco, se pinta de plomo (#B0B0B0); si no, se deja blanca.
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
st.title("Generador de Crucigrama y Sopa de Letras")

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
    
    # --- CRUCIGRAMA ---
    cw_grid, cw_placements = generate_crossword(input_words, grid_size=16)
    cw_buf = grid_to_image(cw_grid)
    
    st.subheader("Crucigrama (20x20)")
    st.image(cw_buf, caption="Crucigrama", use_container_width=True)
    st.download_button("Descargar Crucigrama (PNG)", data=cw_buf, file_name="crucigrama.png", mime="image/png")
    
    st.subheader("Detalle de Palabras en el Crucigrama:")
    info = ""
    for word, r, c, orient in cw_placements:
        orient_str = "Horizontal" if orient == 'H' else "Vertical"
        info += f"{word}: fila {r+1}, col {c+1} ({orient_str})\n"
    st.text(info)
