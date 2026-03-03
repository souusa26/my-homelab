# 🏠 My Homelab Architecture

Repositório dedicado à documentação da minha infraestrutura pessoal rodando em Ubuntu Server. Este projeto serve como meu ambiente de testes para Docker, automação residencial e gestão de serviços de rede.

## 🛠️ Hardware & SO

* **Host:** Dell Latitude 3420 (Notebook atuando como servidor)
* **CPU:** 11th Gen Intel i7-1165G7 (8 cores) @ 4.700GHz
* **RAM:** 16GB DDR4
* **Armazenamento:** 500GB SSD NVMe
* **SO:** Ubuntu 24.04.3 LTS (Noble Numbat)
* **Kernel:** 6.8.0-101-generic

---

## 🐋 Docker Stack & Services

Todos os serviços abaixo são gerenciados via Docker, garantindo isolamento e facilidade no deploy.

| Serviço | Função | Status |
| :--- | :--- | :--- |
| **Homepage** | Dashboard visual de navegação | Up |
| **Home Assistant** | Central de automação residencial | Up |
| **Plex** | Servidor de mídia e streaming | Up |
| **Sonarr / Radarr** | Automação e gestão de bibliotecas de vídeo | Up |
| **Prowlarr** | Gestão de indexadores e busca | Up |
| **AdGuard Home** | DNS Sinkhole e bloqueio de anúncios | Up |
| **Go2RTC** | Gerenciamento de câmeras em tempo real | Up |
| **Tailscale** | Rede mesh VPN para acesso remoto seguro | Up |

---

## 📐 Network Layout (Visual)

```mermaid
graph TD
    Internet((Internet)) --> Tailscale[Tailscale VPN]
    Tailscale --> Server[Ubuntu Server - 192.168.100.65]
    
    subgraph "Docker Containers"
    Server --> Dashboard[Homepage]
    Server --> Automation[Home Assistant]
    Server --> Media[Plex / Arr Stack]
    end
    DNS[AdGuard Home] -.-> |Filtra Rede| Server
