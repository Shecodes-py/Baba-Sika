import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { UssdSimulator } from "@/components/ussd/UssdSimulator";

export const metadata = {
  title: "BabaSika — USSD demo",
};

export default function UssdPage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <Link href="/" className="text-sm text-muted hover:text-foreground">
            ← Home
          </Link>

          <div className="mt-6 grid items-start gap-10 md:grid-cols-2">
            <div>
              <span className="inline-flex items-center gap-2 rounded-full bg-forest-100 px-4 py-1.5 text-sm font-bold text-forest-800">
                📟 No data required
              </span>
              <h1 className="mt-5 font-display text-3xl font-extrabold tracking-tight text-balance text-foreground sm:text-5xl">
                BabaSika on USSD
              </h1>
              <p className="mt-4 text-lg text-muted">
                No smartphone, no data, no app. Any phone can dial *347# and
                save for retirement in seconds — same pension, same 40/60 split.
              </p>
              <p className="mt-4 text-sm leading-6 text-muted">
                This is a live simulator. Tap the keypad to try it: dial{" "}
                <span className="font-mono font-bold text-foreground">*347#</span>,
                press <span className="font-bold text-foreground">Send</span>,
                then follow the menu.
              </p>
              <ul className="mt-6 space-y-2 text-sm text-muted">
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 text-success">✔</span> Works on any phone
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 text-success">✔</span> Check balance, save, log income
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 text-success">✔</span> Confirmed with your PIN
                </li>
              </ul>
            </div>

            <UssdSimulator />
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}