import os
import random
from typing import Any, List, Optional, Tuple

import pandas as pd

class ImportadorDePersonagens:
    """
    Custom node para ComfyUI que importa personagens de uma planilha Excel.
    Seleciona aleatoriamente um personagem baseado em filtros e retorna suas informações.
    """

    COLUNA_E_NOMES = [
        "styleLora",
        "style_lora",
        "style_lora_id",
        "style_lora_uri",
        "Unnamed: 4",
        "coluna_e",
        "Column E",
        "column_e",
        "Coluna E",
        "E",
        "e",
        "item_e",
        "Item E",
        "column5",
    ]
    COLUNA_F_NOMES = [
        "styleName",
        "style_name",
        "styleLoraName",
        "style_lora_name",
        "Unnamed: 5",
        "coluna_f",
        "Column F",
        "column_f",
        "Coluna F",
        "F",
        "f",
        "item_f",
        "Item F",
        "column6",
    ]
    COLUNA_E_INDICE = 4
    COLUNA_F_INDICE = 5
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
                "genero": (["any", "girl", "boy"], {
                    "default": "any"
                }),
                "quantidade": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 17,
                    "step": 1
                }),
            },
            "optional": {
                "filter": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Digite uma palavra para filtrar (ex: naruto)"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("tags_rule", "civitai_id", "character_tags", "outfits", "pixiv_tag", "item_e", "item_f")
    OUTPUT_IS_LIST = (False, False, False, True, False, False, False)
    FUNCTION = "importar_personagem"
    CATEGORY = "Arakis/Importadores"
    
    def __init__(self):
        self.df = None
        self.excel_path = None
    
    def carregar_planilha(self):
        """Carrega a planilha Excel se ainda não foi carregada ou se foi modificada."""
        # Caminho para o arquivo Excel na mesma pasta do código
        current_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(current_dir, "characterListWithStyle.xlsx")
        
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Arquivo characterList2.xlsx não encontrado em: {excel_path}")
        
        # Verifica se precisa recarregar a planilha
        if self.df is None or self.excel_path != excel_path:
            try:
                self.df = pd.read_excel(excel_path)
                self.excel_path = excel_path
                print(f"Planilha carregada com sucesso: {len(self.df)} personagens encontrados")
            except Exception as e:
                raise Exception(f"Erro ao carregar a planilha: {str(e)}")
    
    def processar_civitai_id(self, civitai_id: Any, prefixo: str = "urn:air:sdxl:lora:civitai:") -> str:
        """Normaliza IDs do Civitai removendo prefixos e retornando o sufixo identificador."""
        if civitai_id is None or (isinstance(civitai_id, float) and pd.isna(civitai_id)):
            return ""

        civitai_str = str(civitai_id).strip()

        if not civitai_str or civitai_str.lower() == "nan":
            return ""

        if prefixo and civitai_str.startswith(prefixo):
            return civitai_str[len(prefixo):]

        if "civitai:" in civitai_str:
            return civitai_str.split("civitai:", 1)[1]

        if "civitai/" in civitai_str:
            return civitai_str.split("civitai/", 1)[1]

        if civitai_str.startswith("urn:") and ":" in civitai_str:
            return civitai_str.split(":")[-1]

        return civitai_str

    def obter_valor_coluna(self, linha: pd.Series, possiveis_nomes: List[str], indice_padrao: Optional[int]) -> str:
        """Retorna o valor limpo da coluna considerando nomes alternativos ou índice."""
        for nome in possiveis_nomes:
            if nome in linha.index:
                valor = linha.get(nome)
                if pd.isna(valor):
                    continue
                valor_str = str(valor).strip()
                if not valor_str or valor_str.lower() == "nan":
                    continue
                return valor_str

        if indice_padrao is not None and 0 <= indice_padrao < len(linha):
            valor = linha.iloc[indice_padrao]
            if not pd.isna(valor):
                valor_str = str(valor).strip()
                if valor_str and valor_str.lower() != "nan":
                    return valor_str

        return ""
    
    def coletar_outfits(self, linha: pd.Series, quantidade: int) -> List[str]:
        """Coleta os outfits disponíveis da linha e seleciona aleatoriamente a quantidade desejada."""
        # Colunas de outfit vão de outfit_1 até outfit_17
        outfit_cols = [f"outfit_{i}" for i in range(1, 18)]
        
        # Coleta todos os outfits não vazios
        outfits_disponiveis = []
        for col in outfit_cols:
            if col in linha.index and not pd.isna(linha[col]) and str(linha[col]).strip():
                outfits_disponiveis.append(str(linha[col]).strip())
        
        # Se não há outfits disponíveis, retorna lista vazia
        if not outfits_disponiveis:
            return []
        
        # Se a quantidade solicitada é maior que os outfits disponíveis, repete os outfits
        outfits_selecionados = []
        for _ in range(quantidade):
            outfit_escolhido = random.choice(outfits_disponiveis)
            outfits_selecionados.append(outfit_escolhido)
        
        return outfits_selecionados
    
    def filtrar_dataframe(self, df: pd.DataFrame, filtro: str, genero: str) -> pd.DataFrame:
        """Aplica os filtros ao dataframe."""
        df_filtrado = df.copy()
        
        # Filtro por TAGS RULE (coluna A)
        if filtro and filtro.strip():
            filtro_lower = filtro.lower().strip()
            # Filtra por linhas que contêm a palavra na coluna TAGS RULE
            mask_tags = df_filtrado['TAGS RULE'].astype(str).str.lower().str.contains(filtro_lower, na=False)
            df_filtrado = df_filtrado[mask_tags]
        
        # Filtro por gênero (coluna sexo)
        if genero != "any":
            # Filtra por linhas que correspondem ao gênero selecionado
            mask_genero = df_filtrado['sexo'].astype(str).str.lower() == genero.lower()
            df_filtrado = df_filtrado[mask_genero]
        
        return df_filtrado
    
    @classmethod
    def IS_CHANGED(cls, seed, genero, quantidade, filter=""):
        # Sempre retorna um valor diferente para forçar execução
        return float("nan")
    
    def importar_personagem(self, seed: int, genero: str, quantidade: int, filter: str = "") -> Tuple[str, str, str, List[str], str, str, str]:
        """Função principal que executa a lógica do node."""
        try:
            # Define o seed para garantir aleatoriedade verdadeira baseada no valor do seed
            random.seed(seed)
            
            # Carrega a planilha
            self.carregar_planilha()
            
            # Aplica os filtros
            df_filtrado = self.filtrar_dataframe(self.df, filter, genero)
            
            # Verifica se há resultados após a filtragem
            if df_filtrado.empty:
                return ("Nenhum personagem encontrado com os filtros aplicados", "", "", [], "", "", "")
            
            # Seleciona uma linha aleatória
            linha_selecionada = df_filtrado.sample(n=1).iloc[0]
            
            # Extrai as informações
            tags_rule = str(linha_selecionada.get('TAGS RULE', ''))
            civitai_id_raw = linha_selecionada.get('CIVITAI ID', '')
            civitai_id = self.processar_civitai_id(civitai_id_raw)
            character_tags = str(linha_selecionada.get('character_tags', ''))
            pixiv_tag = str(linha_selecionada.get('pixiv_tag', '')).strip()
            item_e_bruto = self.obter_valor_coluna(
                linha_selecionada,
                self.COLUNA_E_NOMES,
                self.COLUNA_E_INDICE,
            )
            item_f = self.obter_valor_coluna(
                linha_selecionada,
                self.COLUNA_F_NOMES,
                self.COLUNA_F_INDICE,
            )
            item_e = self.processar_civitai_id(item_e_bruto)

            # Coleta os outfits como lista de strings
            outfits_lista = self.coletar_outfits(linha_selecionada, quantidade)

            return (tags_rule, civitai_id, character_tags, outfits_lista, pixiv_tag, item_e, item_f)

        except Exception as e:
            error_msg = f"Erro no ImportadorDePersonagens: {str(e)}"
            print(error_msg)
            return (error_msg, "", "", [], "", "", "")

