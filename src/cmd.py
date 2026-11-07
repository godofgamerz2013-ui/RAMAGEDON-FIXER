"""ApexRig-AI terminal mode."""
import getpass
import keyring
from engine import scan_processes, ask_gemini, log


def main():
    print("\nAPEXRIG-AI | CMD MODE")
    print("--------------------")
    key = keyring.get_password("ApexRig-AI", "gemini") or ""
    if not key:
        key = getpass.getpass("Gemini API key: ").strip()
        if not key:
            print("No API key entered.")
            input("Press ENTER to exit...")
            return
        keyring.set_password("ApexRig-AI", "gemini", key)

    print("\nScanning processes and asking Gemini...")
    log("CMD mode analysis started.")
    try:
        processes = scan_processes()
        recommendations = ask_gemini(processes, key)
        names = {p["pid"]: p["name"] for p in processes}
        print("\nRESULTS")
        print("-------")
        if not recommendations:
            print("No process recommendations. Your system looks good.")
        for item in recommendations:
            print(f"\n{names.get(item['pid'], 'Unknown')} | PID {item['pid']}")
            print(item.get("reason", "No reason supplied."))
        print("\nNo processes were changed.")
        log(f"CMD mode returned {len(recommendations)} recommendations.")
    except Exception as exc:
        print(f"\nAnalysis failed: {exc}")
        log("CMD mode analysis failed: " + str(exc))
    input("\nPress ENTER to close...")


if __name__ == "__main__":
    main()
