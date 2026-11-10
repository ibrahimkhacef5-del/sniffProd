import sys
from .core import scan, color

BANNER = r"""
  ███████╗███╗   ██╗██╗███████╗███████╗███████╗██████╗ 
  ██╔════╝████╗  ██║██║██╔════╝██╔════╝██╔════╝██╔══██╗
  ███████╗██╔██╗ ██║██║█████╗  █████╗  █████╗  ██████╔╝
  ╚════██║██║╚██╗██║██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗
  ███████║██║ ╚████║██║██║     ██║     ███████╗██║  ██║
  ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
"""

def help_text():
    print(color(BANNER, "c"))
    print(color("  Sniffer - أداة فحص وتحميل ملفات المواقع\n", "y"))
    print("الاستخدام:")
    print("  sniffer <url>              ← فحص وتحميل ملفات الموقع")
    print("  sniffer <url> -o <dir>     ← تحديد مجلد الحفظ")
    print("  sniffer info               ← عرض هذه الرسالة\n")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        help_text()
        sys.exit(0)

    url = sys.argv[1]
    out_dir = None

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            out_dir = sys.argv[idx + 1]

    scan(url, out_dir)

if __name__ == "__main__":
    main()
