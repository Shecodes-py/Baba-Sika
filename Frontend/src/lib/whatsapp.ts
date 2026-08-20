const DEFAULT_MESSAGE = "Hi BabaSika, I'd like to start saving for my pension.";

/** Builds a click-to-chat WhatsApp link from the configured business number. */
export function getWhatsAppLink(message: string = DEFAULT_MESSAGE): string {
  const number = (process.env.NEXT_PUBLIC_WHATSAPP_NUMBER ?? "").replace(/[^\d]/g, "");
  const text = encodeURIComponent(message);
  if (!number) return `https://wa.me/?text=${text}`;
  return `https://wa.me/${number}?text=${text}`;
}
