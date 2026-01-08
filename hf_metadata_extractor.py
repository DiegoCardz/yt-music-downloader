#%%
import os
import requests
import ast

hf_token = os.getenv("HF_TOKEN")
if hf_token:
    print("✅ HF_TOKEN found and set.")
else:
    raise ValueError("❌ HF_TOKEN environment variable not set.")

# %% # Function to set up HF API query
API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {hf_token}",
}
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# %% # Function to extract metadata using the HF model
def extract_metadata_from_description(song_description: str, model:str="zai-org/GLM-4.7:novita") -> dict:
    """
    Extract metadata from song description using a Hugging Face language model.
    """
    response = query({
        "messages": [
            {
                "role": "system",
                "content":f""" 
                    You are an assistant who reads information on the description of a song
                    and provides accurate information about it, focusing on metadata such as
                    artist, album, release date, and genre.
                    """
            },
            {
                "role": "user",
                "content": f"""
                Given the following song description, extract the metadata including 
                artist, participating artists, album, original song, composers, 
                release year, and genre.
        
                Song Description:
                {song_description}
        
                Expected Metadata:
                A python dictionary with the following keys and their corresponding values:
                'Track', 'Artist', 'Participating Artists', 'Album', 'Original song', 'Composers', 'Release Year', 'Genre'.
                
                Guidelines:
                - Include all the keys even if some values are None.
                - If any field contains more than one item, separate them by semi-colons (;).
                - For 'Track', look in the description for the real title of the song, not the video title.
                Also, do not include any extra information such as "cover", "live", "Ao vivo", "official video", etc.
                This extra information can be used for Album if more precise album info were not found.
                - For 'Participating Artists', be sure to include the main artist. Also include 
                featured artists mentioned in the description.
                - For 'Original song', try looking preferably for an international version of the song
                refered in the description, sopecially if the composer names are international.
                - For 'Album', if no album name is found, you can use "Single", "Ao Vivo", "Cover",
                "Official video" or any other term used to complement the track name found in the 
                title or somewhere else in the description.
                - If any metadata is missing, fill it with None (the None python value).
                """
            },
        ],
        "model": model
    })

    response_str = response["choices"][0]["message"]["content"]


    dict_str = response_str.strip().replace('```python\n', '').replace('\n```', '')
    derived_metadata_dict = ast.literal_eval(dict_str)
    
    return derived_metadata_dict

#%%
def print_extracted_metadata(derived_metadata_dict: dict):
    print("LLM Extracted Metadata:")
    for key, val in derived_metadata_dict.items():
        print(f"{str(key)[:24]:-<25}{str(val)[:45]}")


#%%
if __name__ == "__main__":
    song_description = """
    ▸ Assista minha playlist de músicas: https://onilnk.com/r/DiegoPerensin_Tu...  
    ▸ Inscreva-se no canal:  https://onilnk.com/r/DiegoPerensin

    Cover da Música "Te Louvo" de Marcus Salles feat. Brunão Morada, interpretada por Diego Perensin feat. Nazareno Central Music.

    ▸ Letra - Te Louvo (We Praise You)

    Compositores: Brandon Aaronson / Brian Johnson / Phil Wickham / Matt Redman

    Meus inimigos se calam quando eu louvo
    A ansiedade acaba quando eu louvo
    Louvarei, Te louvarei
    Teu nome eu canto
    E tudo se transforma
    Com força eu proclamo Tua vitória
    Louvarei, Te louvarei

    Gigantes não resistirão
    Barreiras vão ao chão
    O medo se desfaz quando eu louvo
    Eu sei que Deus comigo está
    Pra sempre reinará
    Com toda a criação
    Eu Te louvo
    Oh, Te Louvo
    Oh, Te Louvo

    Com fé eu canto
    E vejo o mar se acalmar
    Com fé eu canto
    E sinto em mim a Tua paz
    Louvarei, Te louvarei

    Só em Ti tenho vida
    Só em Ti eu sou livre
    Junto com os céus eu canto
    Te louvo, Te louvo

    ▸ Outras músicas do Diego Perensin:

    Farás Um Caminho: https://onilnk.com/r/DiegoPerensin_Fa... 
    Tua Presença é o Céu Pra Mim + Alfa e Ômega: https://onilnk.com/r/DiegoPerensin_Tu... 
    Foi Certeiro: https://onilnk.com/r/DiegoPerensin_Fo... 
    O Que Dizer: https://onilnk.com/r/DiegoPerensin_OQ... 
    É Tudo Sobre Você: https://onilnk.com/r/DiegoPerensin_ET... 
    Faça Morada: https://onilnk.com/r/DiegoPerensin_Fa... 
    Os Sonhos de Deus: https://onilnk.com/r/DiegoPerensin_Os... 
    Todavia me Alegrarei: https://onilnk.com/r/DiegoPerensin_To... 

    ▸ Diego Perensin, nascido em Juiz de Fora/MG, é um jovem músico, tecladista, ministro e produtor musical que hoje reside na cidade de Campinas/SP. Filho de pastor, Diego iniciou cantando na igreja aos 3 anos de idade, acompanhando seu pai nos diversos lugares em que ia pregar. Aos 6 anos iniciou suas aulas de piano no conservatório de sua cidade, aos 8 começou seus estudos de piano popular, instrumento este que posteriormente seria seu instrumento de formação na Universidade de Música Popular Brasileira Bituca de Barbacena/MG e se formou aos 18 anos, no ano de 2010. Iniciou com 9 anos no ministério de louvor de sua igreja local como tecladista e back vocal, o qual, anos mais tarde, viria a liderar. Durante sua adolescência começou a compor músicas e a cantar.

    Em 2020, retoma seu trabalho solo em parceria com a Onimusic, seguindo com a missão de propagar a mensagem do evangelho e do amor de Deus através da música, além de fortalecer ainda mais seu chamado para abençoar e inspirar músicos e líderes de louvor de Igrejas locais que têm buscado vivenciar o ministério de forma santa e excelente. 

    Ouça o último lançamento: “Tudo é Possível”

    ▸Oni@1526!, Diego Perensin, Nazareno Central Music, Te Louvo, We Praise You, Gospel, Hinos 2023, Diego Perensin 2023, Nazareno Central Music 2023, Te Louvo 2023, We Praise You 2023, Worship, Louvores 2023, Louvores de Adoração.

    ▸‪@DiegoPerensinOficial‬ vem com seu novo single #TeLouvo juntamente com Nazareno Central Music. Ele também nos traz muitas outras canções maravilhosas e parcerias incríveis como, Tudo é Possível e Vitorioso És com Nazareno Central Music, Tua Presença é o Céu Pra Mim + Alfa e Ômega com Com Cristo, Farás Um Caminho com Viviane Perensin entre outras músicas.

    ▸ Ficha Técnica 

    Direção Geral e Executiva: Igreja do Nazareno Central de Campinas/SP
    Direção de Vídeo: Igreja do Nazareno Central de Campinas/SP
    -
    Produção Musical: Diego Perensin
    Mix: Renan Moraes 
    Corte: TG Alves 
    Cor e Motion: Leonardo Cirqueira 
    Direção de culto: William Camilloti 
    -
    Ministração: Diego Perensin
    Bateria: Guilherme Miguel 
    Baixo: Jonatas Depret 
    Teclados: Kelio Silva, Eduardo Bortolatto
    Guitarras: Giovani Campos e Rodrigo Camargo 
    Vocal: Bianca Valencio, Miliane Souza, Fabiana Duarte, Ivan Rodrigues, Jediael Damasceno, Ana Paula Assis;
    Arranjo e preparação vocal: Eli Teixeira

    ▸ Saiba mais sobre o Diego Perensin em: 
    Instagram: https://onilnk.com/r/InstagramDiegoPe...
    Facebook: https://onilnk.com/r/FacebookDiegoPer...

    #DiegoPerensin #NazarenoCentralMusic #TeLouvo #WePraiseYou #SomQueAlimenta
    """
    song_metadata = """
    Artist: Diego Perensin
    Participating Artists: Diego Perensin, Nazareno Central Music
    Album: Ao Vivo
    Original song: We Praise You
    Composers: Brandon Aaronson, Brian Johnson, Phil Wickham, Matt Redman
    Release Year: 2023
    Genre: Gospel, Worship
    """
    
    extracted_metadata = extract_metadata_from_description(song_description)
    print_extracted_metadata(extracted_metadata)