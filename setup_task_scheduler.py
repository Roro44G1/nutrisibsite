import os
import sys
import subprocess
from pathlib import Path

# ============================================
#  CONFIGURARE TASK SCHEDULER WINDOWS
#  Ruleaza agent_context.py saptamanal
#  Ruleaza acest script O SINGURA DATA
# ============================================

# ── Configurare ──
NUME_TASK = "NutriSib_Regenerare_Context"
SCRIPT = Path(__file__).parent / "agent_context.py"
ZI_SAPTAMANA = "MON"   # MON, TUE, WED, THU, FRI, SAT, SUN
ORA = "08:00"          # ora la care ruleaza

# ============================================

def verifica_python():
    """Gaseste calea exacta spre Python"""
    return sys.executable

def creeaza_task():
    python_exe = verifica_python()

    if not SCRIPT.exists():
        print(f"\n  EROARE: Nu gasesc {SCRIPT}")
        print("  Asigura-te ca agent_context.py e in acelasi folder.")
        input("\n  Apasa Enter...")
        return False

    print(f"\n  Python:  {python_exe}")
    print(f"  Script:  {SCRIPT}")
    print(f"  Rulare:  In fiecare {ZI_SAPTAMANA} la {ORA}")

    # Comanda schtasks pentru creare task
    cmd = [
        "schtasks", "/create",
        "/tn", NUME_TASK,
        "/tr", f'"{python_exe}" "{SCRIPT}"',
        "/sc", "WEEKLY",
        "/d", ZI_SAPTAMANA,
        "/st", ORA,
        "/f",  # suprascrie daca exista
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False
        )

        if result.returncode == 0:
            print(f"\n  Task creat cu succes!")
            return True
        else:
            print(f"\n  Eroare: {result.stderr}")
            return False

    except Exception as e:
        print(f"\n  Exceptie: {e}")
        return False

def sterge_task():
    """Sterge taskul daca exista"""
    cmd = ["schtasks", "/delete", "/tn", NUME_TASK, "/f"]
    subprocess.run(cmd, capture_output=True)
    print(f"  Task '{NUME_TASK}' sters.")

def verifica_task():
    """Verifica daca taskul exista"""
    cmd = ["schtasks", "/query", "/tn", NUME_TASK]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def ruleaza_acum():
    """Ruleaza taskul imediat pentru test"""
    cmd = ["schtasks", "/run", "/tn", NUME_TASK]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("  Task pornit! Verifica fereastra care apare.")
    else:
        print(f"  Eroare: {result.stderr}")

def main():
    print("\n" + "="*55)
    print("  CONFIGURARE TASK SCHEDULER — NutriSib")
    print("="*55)

    # Verifica daca taskul exista deja
    if verifica_task():
        print(f"\n  Taskul '{NUME_TASK}' exista deja!")
        print("\n  Ce vrei sa faci?")
        print("  1. Recreaza taskul (suprascrie)")
        print("  2. Sterge taskul")
        print("  3. Ruleaza acum pentru test")
        print("  4. Iesire")

        alegere = input("\n  Alegere (1-4): ").strip()

        if alegere == "1":
            creeaza_task()
        elif alegere == "2":
            sterge_task()
        elif alegere == "3":
            ruleaza_acum()
        else:
            print("  Iesire.")
    else:
        print(f"\n  Taskul nu exista inca. Il cream acum...")
        if creeaza_task():
            print(f"\n  Rezumat:")
            print(f"  Nume task:  {NUME_TASK}")
            print(f"  Frecventa:  Saptamanal, in fiecare {ZI_SAPTAMANA}")
            print(f"  Ora:        {ORA}")
            print(f"  Script:     {SCRIPT}")
            print(f"\n  Poti vedea taskul in:")
            print(f"  Start → Task Scheduler → Task Scheduler Library")
            print(f"\n  Vrei sa il testezi acum? (d/n): ", end="")
            if input().strip().lower() in ["d", "da", "y"]:
                ruleaza_acum()

    print("\n  IMPORTANT: Dupa fiecare rulare automata,")
    print("  context_site.js se actualizeaza local.")
    print("  Nu uita sa faci commit + push pe GitHub!")
    print("\n  Alternativa: adauga un GitHub Action pentru push automat.")

    input("\n  Apasa Enter pentru a inchide...")

if __name__ == "__main__":
    main()
