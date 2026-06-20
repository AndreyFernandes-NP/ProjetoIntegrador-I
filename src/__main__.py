from __future__ import annotations

import sys
import os

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.pipeline import pipeline
from src.mlearn.pipeline import supervised_pipeline, unsupervised_pipeline, run_mlearn

# Classes
@dataclass
class MenuOption:
    label: str
    action: Callable[..., Any] | None = None
    params: dict[str, Any] = field(default_factory=dict)
    exit_program: bool = False

@dataclass
class MenuResult:
    command: str
    next_menu: dict[int, MenuOption] | None = None

# Database de Opções
MAIN_MENU: dict[int, MenuOption] = {
    1: MenuOption(
        label="Acessar aba de Pipeline de Dados",
        action=lambda: open_pipeline(),
        params={}
    ),
    2: MenuOption(
        label="Acessar aba de Modelos de Machine Learning",
        action=lambda: open_models(),
        params={}
    ),
    3: MenuOption(
        label="Encerrar o Programa",
        action=lambda: exit_program(),
        params={}
    )
}

PIPELINE_MENU = {
    1: MenuOption(
        label="Atualizar dataframe com fontes novas",
        action=pipeline,
        params={"force_save": False}
    ),
    2: MenuOption(
        label="Atualizar/criar os dataframes",
        action=pipeline,
        params={"force_save": True}
    ),
    3: MenuOption(
        label="Voltar",
        action=lambda: back()
    )
}

MODELS_MENU = {
    1: MenuOption(
        label="Executar modelos não-supervisionados",
        action=unsupervised_pipeline,
        params={}
    ),
    2: MenuOption(
        label="Executar modelos supervisionados",
        action=supervised_pipeline,
        params={}
    ),
    3: MenuOption(
        label="Executar todos",
        action=run_mlearn,
        params={}
    ),
    4: MenuOption(
        label="Voltar",
        action=lambda: back()
    )
}

# Helpers das Classes
def stay():
    return MenuResult(command="stay")

def go_to(menu: dict[int, MenuOption]):
    return MenuResult(command="go_to", next_menu=menu)

def back():
    return MenuResult(command="back")

def exit_program():
    return MenuResult(command="exit")

# Função de Opções
def select_option(options: dict[int, MenuOption], prompt_message: str) -> MenuOption | None:
    for key, option in options.items():
        print(f"{key} - {option.label}")

    choice = ask_prompt(prompt_message)

    return options.get(choice)

def open_pipeline():
    return go_to(PIPELINE_MENU)

def open_models():
    return go_to(MODELS_MENU)

# Funções do Terminal
def clr() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def ask_prompt(prompt_message: str = "") -> int:
    value = input(prompt_message).strip()

    if value == "":
        return 0
    
    try:
        n = int(value)
        return n

    except ValueError as e:
        print(f"[Erro] O valor inserido deve ser um número inteiro, por favor, digite novamente.")
        return -1

def print_logo() -> None:
    print("-"*45)
    print("-"*15 + "[ Sistema IDS ]" + "-"*15)
    print("-"*45)

# main
def main():
    menu_stack = []
    current_menu = MAIN_MENU

    while True:
        clr()
        print_logo()

        option = select_option(
            current_menu,
            "Digite o número de uma das opções acima: "
        )

        if option is None:
            print("[Erro] Opção inválida.")
            ask_prompt("Pressione Enter para continuar...")
            continue

        if option.action is None:
            print("[Erro] Nenhuma ação configurada para essa opção.")
            ask_prompt("Pressione Enter para continuar...")
            continue

        try:
            result = option.action(**option.params)

            if result is None:
                ask_prompt("Pressione Enter para continuar...")
                continue
            
            match result.command:
                case "stay":
                    ask_prompt("Pressione Enter para continuar...")
                
                case "go_to":
                    menu_stack.append(current_menu)
                    current_menu = result.next_menu
                
                case "back":
                    if menu_stack:
                        current_menu = menu_stack.pop()
                    else:
                        current_menu = MAIN_MENU

                case "exit":
                    print("Encerrando programa...")
                    break
                
                case _:
                    ask_prompt("Pressione Enter para continuar...")
                
        except Exception as e:
            print("[Erro] Ocorreu um erro durante a execução do programa, faça sua escolha novamente.")
            print(f"[Debug] {type(e).__name__}: {e}")
            ask_prompt("Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
