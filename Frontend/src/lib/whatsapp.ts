// While running on Twilio's shared WhatsApp Sandbox, a phone has to send the
// join code as its very first message before Twilio forwards anything else
// to our webhook - so the click-to-chat link's prefilled text IS the join
// code, not a greeting. Once a dedicated WhatsApp Business number replaces
// the sandbox, NEXT_PUBLIC_WHATSAPP_SANDBOX_CODE can just be unset.
const SANDBOX_CODE = process.env.NEXT_PUBLIC_WHATSAPP_SANDBOX_CODE ?? "";

export function isSandboxMode(): boolean {
  return SANDBOX_CODE.length > 0;
}

/** Builds a click-to-chat WhatsApp link from the configured business number. */
export function getWhatsAppLink(message?: string): string {
  const number = (process.env.NEXT_PUBLIC_WHATSAPP_NUMBER ?? "").replace(/[^\d]/g, "");
  const text = encodeURIComponent(message ?? SANDBOX_CODE ?? "Hi BabaSika, I'd like to start saving for my pension.");
  if (!number) return `https://wa.me/?text=${text}`;
  return `https://wa.me/${number}?text=${text}`;
}
