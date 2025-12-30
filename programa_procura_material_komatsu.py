import pandas as pd
import streamlit as st

# ================================================================================================================ #
try:
    database = pd.read_csv(
    "https://raw.githubusercontent.com/pedddrym/base_de_dados_programa_procura-material-komatsu/main/PRECOS.CSV",
    sep=";",
    encoding="latin1"
    )
except Exception as e:
    st.error(body="Ocorreu um erro ao ler o arquivo csv: {e}", icon="⚠️")
# ================================================================================================================ #

st.title("PROCURADOR DE MATERIAL KOMATSU", text_alignment="center", width="stretch")

k_code = st.text_input(
    label="Digite o código KOMATSU do material (Pressione Enter)",
    icon="🔎",
    help="Pode pesquisar ou pelo código KOMATSU ou pelo nome do material"
)

# ============================================================================= #
def search(term: str, df: pd.DataFrame) -> tuple:
    """ 
    Procura o material no DataFrame.
    Retorna (TIPO_DE_RESULTADO, DADOS)
    Tipo: "CODE" -> Acha 1 item pelo código exato.
    Tipo: "DESC" -> Acha múltiplos itens pela descrição.
    Tipo: None   -> Não acha nada.
    """
    term = term.upper().strip()
    material_df = df[df[ df.columns[0] ] == term]

    if not material_df.empty:
        data = material_df.iloc[0]
        result_tuple = tuple()
        for col in material_df.columns:
            result_tuple += (data.get(col, ''),)
        
        return ("CODE", [result_tuple])
    
    for col in material_df.columns:
        if "Desc" in col:
            desc = col
    
    desc_df = df[df[desc].str.contains(term, case=False, na=False)]
    code_df = df[df[df.columns[0]].str.contains(term, case=False, na=False)]

    if not desc_df.empty:   # Achou o material produto pela descrição
        if len(desc_df) > 15:
            return ("DESC", desc_df.sample(n=15))
        else:
            return ("DESC", desc_df)
    elif not code_df.empty: # Achou o material por parte do código
        if len(code_df) > 15:
            return ("DESC", code_df.sample(n=15))
        else:
            return ("DESC", code_df)
    
    # Se nada tiver sido encontrado:
    st.error(body="ERRO! Material não encontrado!", icon="⚠️")
    raise LookupError("Imput data not found in the given database")
# ============================================================================= #

# ============================================================================= #
def return_search():
    result_type, result_data = search(term=k_code, df=database)
    if isinstance(result_data, list):
        result_tuple = result_data[0]
    else:
        result_tuple = result_data.iloc[0]
    
    left_column, right_column = st.columns(2)

    if result_type == "CODE":
        columns = database.columns
        for i, (label_txt, item) in enumerate(zip(columns, result_tuple)):
            left_column.text(body=label_txt)
            if "," in item and ("V" in label_txt or "P" in label_txt and not "Líquido" in label_txt):
                right_column.text(body=f"R$ {item}")
            else:
                right_column.text(body=item)
    
    elif result_type == "DESC":
        st.dataframe(
            result_data[[result_data.columns[0], result_data.columns[1]]],
            hide_index=True
        )

if k_code:
    st.header(body="Material(is) encontrado(s)", text_alignment="center")
    st.divider()
    return_search()
