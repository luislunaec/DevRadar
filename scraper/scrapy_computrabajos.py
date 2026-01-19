import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


class RecolectorComputrabajo:
    def __init__(self, roles):
        self.base_url = "https://ec.computrabajo.com"
        self.roles = roles
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.datos = []

    def recolectar(self, paginas_por_rol=3):
        for rol in self.roles:
            print(f"Buscando links para: {rol}")
            slug = rol.replace(" ", "-")

            for p in range(1, paginas_por_rol + 1):
                url = f"{self.base_url}/trabajo-de-{slug}?p={p}"
                try:
                    res = requests.get(url, headers=self.headers, timeout=10)
                    if res.status_code != 200:
                        break

                    soup = BeautifulSoup(res.content, 'html.parser')
                    ofertas = soup.find_all('article', class_='box_offer')

                    for oferta in ofertas:
                        titulo_tag = oferta.find('h2')
                        if not titulo_tag:
                            continue

                        link = self.base_url + titulo_tag.find('a')['href']
                        empresa = (
                            oferta.find('p', class_='fs16').get_text(strip=True)
                            if oferta.find('p', class_='fs16')
                            else "N/A"
                        )
                        locacion = (
                            oferta.find('p', class_='fs13').get_text(strip=True)
                            if oferta.find('p', class_='fs13')
                            else "Ecuador"
                        )
                        fecha = (
                            oferta.find('span', class_='fc_aux').get_text(strip=True)
                            if oferta.find('span', class_='fc_aux')
                            else "Reciente"
                        )

                        sueldo = "No especificado"
                        info_extras = oferta.find_all('span', class_='mr10')
                        for info in info_extras:
                            if '$' in info.text:
                                sueldo = info.text.strip()

                        self.datos.append({
                            'fecha_publicacion': fecha,
                            'oferta_laboral': titulo_tag.get_text(strip=True),
                            'compania': empresa,
                            'locacion': locacion,
                            'sueldo': sueldo,
                            'url_publicacion': link,
                            'rol_busqueda': rol
                        })

                    print(f"Página {p} procesada.")
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"Error en página {p}: {e}")

        self.guardar_csv()

    def guardar_csv(self):
        df = pd.DataFrame(self.datos)
        df.drop_duplicates(subset=['url_publicacion'], inplace=True)
        df.to_csv("ofertas_crudas.csv", index=False, encoding='utf-8-sig')
        print(f"Recolección terminada. {len(df)} registros guardados en 'ofertas_crudas.csv'")


if __name__ == "__main__":
    roles = [
        "sistemas de información",
        "ingeniero de sistemas",
        "tecnologia",
        "informatica",
        "programador",
        "desarrollador",
        "desarrollador web",
        "backend",
        "frontend",
        "full stack",
        "software",
        "analista de sistemas",
        "analista ti",
        "soporte tecnico",
        "mesa de ayuda",
        "devops",
        "administrador de sistemas",
        "administrador de redes",
        "cloud",
        "qa",
        "tester",
        "ciberseguridad",
        "seguridad informatica",
        "data analyst",
        "data engineer",
        "bases de datos",
        "sql",
        "python",
        "java"
    ]

    bot = RecolectorComputrabajo(roles)
    bot.recolectar(paginas_por_rol=5)
