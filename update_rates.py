# מושך את השער היציג של בנק ישראל (דולר ויורו) ושומר ל-rates.json.
# רץ פעם ביום ב-GitHub Actions. אפשר גם להריץ ידנית: python update_rates.py
import csv, io, json, os, urllib.request, datetime

START = "2024-01-01"
SERIES = {"USD": "RER_USD_ILS", "EUR": "RER_EUR_ILS"}
URL = ("https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/"
       "{code}?startperiod={start}&endperiod={end}&format=csv")

def fetch(code, end):
    req = urllib.request.Request(URL.format(code=code, start=START, end=end), headers={"User-Agent": "invoices-rates"})
    text = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    out = {}
    for row in csv.DictReader(io.StringIO(text)):
        try:
            out[row["TIME_PERIOD"]] = float(row["OBS_VALUE"])
        except (KeyError, ValueError):
            pass
    return out

def main():
    end = datetime.date.today().isoformat()
    data = {"source": "בנק ישראל - שער יציג", "updated": end}
    for cur, code in SERIES.items():
        data[cur] = fetch(code, end)
        if not data[cur]:
            raise SystemExit("no rates for " + cur)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rates.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("USD:", len(data["USD"]), "EUR:", len(data["EUR"]))

if __name__ == "__main__":
    main()
