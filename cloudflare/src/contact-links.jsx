import React from "react";
import { CONTACT_FIELDS, contactLink, normalizePhone, splitValues, whatsappURL } from "../shared/contacts.mjs";

const names = { email: "Email / Gmail", phone: "Phone / WhatsApp", whatsapp: "WhatsApp", facebook: "Facebook", linkedin: "LinkedIn", telegram: "Telegram", contact_url: "Contact page", admin_name: "Contact name" };

export function ContactLinks({ field, value, country = "" }) {
  const values = splitValues(value);
  if (!values.length) return <span className="subtle">Not recorded</span>;
  return <div className="contact-links">{values.map((v, i) => {
    const href = contactLink(field, v, country);
    const web = href.startsWith("https://") || href.startsWith("http://");
    const phone = ["phone", "whatsapp"].includes(field) && normalizePhone(v);
    const wa = phone && whatsappURL(v, country);
    return <div className="contact-link" key={i}>
      {href ? <a href={href} {...(web ? { target: "_blank", rel: "noopener noreferrer" } : {})} aria-label={`${wa ? "Open WhatsApp for" : names[field] || field} ${v}`}>{v}</a> : <span>{v}</span>}
      {phone && wa && <a className="contact-secondary" href={`tel:${phone}`}>Call</a>}
      {field === "email" && href && <a className="contact-secondary" target="_blank" rel="noopener noreferrer" href={`https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(v)}`}>Gmail</a>}
      {phone && !wa && <small className="subtle">Country code needed for WhatsApp</small>}
    </div>;
  })}</div>;
}

export function ContactChannels({ contact, country = "" }) {
  const fields = CONTACT_FIELDS.filter((key) => contact[key]);
  return <dl className="detail-grid">{fields.map((key) => <div key={key}><dt>{names[key]}</dt>
    <dd><ContactLinks field={key} value={contact[key]} country={country} /></dd></div>)}
    {contact.status && <div><dt>Status</dt><dd>{contact.status}</dd></div>}
    {contact.notes && <div><dt>Notes</dt><dd>{contact.notes}</dd></div>}
  </dl>;
}
