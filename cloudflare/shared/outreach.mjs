import { domain, text } from "./domain.mjs";
export function outreach(f, client = false) {
  const site = domain(f.site) || text(f.site) || "your website",
    name = text(f.recipient).split(" ")[0],
    sender = text(f.sender) || "[Your name]",
    company = text(f.company) || "[Your company]",
    role = text(f.role) || "SEO & Outreach Specialist",
    niche = text(f.niche) || "your industry";
  const greeting = `Hi ${name || "there"},`,
    signature = `Best regards,\n${sender}\n${role}\n${company}`;
  const purpose = f.purpose || "Guest Post",
    service = f.service || "SEO + Guest Posting";
  if (client) {
    const benefits = {
      SEO: "improve organic visibility and attract relevant search traffic",
      "Guest Posting":
        "build relevant authority through carefully selected publisher placements",
      "Link Building": "earn niche-relevant backlinks",
      "SEO + Guest Posting":
        "combine on-site SEO improvements with relevant publisher outreach",
      "Content Outreach":
        "expand content reach through publisher relationships",
      "Digital PR / Outreach":
        "build visibility through personalized publisher outreach",
    };
    const benefit = benefits[service] || benefits.SEO,
      observation = text(f.observation)
        ? `While reviewing ${site}, I noticed an opportunity around ${text(f.observation)}.`
        : `I came across ${site} while researching businesses in ${niche} and thought there may be an opportunity to strengthen its SEO and outreach performance.`;
    const intro =
      f.tone === "Friendly"
        ? `I’m ${sender} from ${company}. I work with businesses on ${service.toLowerCase()} to ${benefit}.`
        : `My name is ${sender}, ${role} at ${company}. We help businesses ${benefit}.`;
    return {
      Subject: `${service} opportunity for ${text(f.client_company) || site}`,
      Email: `${greeting}\n\n${observation}\n\n${intro}${text(f.proof) ? "\n\nFor context, " + text(f.proof) : ""}\n\n${text(f.cta) || "Would you be open to a short conversation? I can share a few practical ideas specific to your website first."}\n\n${signature}`,
      "Follow-up 1": `${greeting}\n\nJust following up on my note about ${site}. I’d be happy to share 2–3 ${service.toLowerCase()} ideas specific to your website. Would that be useful?\n\n${signature}`,
      "Follow-up 2": `${greeting}\n\nOne last follow-up regarding ${site}. If ${service.toLowerCase()} is a priority, I’d be glad to share a simple action plan. If the timing isn’t right, no worries.\n\n${signature}`,
      LinkedIn: `Hi ${name || "there"}, I came across ${site} while researching ${niche}. I work in ${service} at ${company} and thought it would be good to connect.`,
      WhatsApp: `Hi ${name || "there"}, this is ${sender} from ${company}. I came across ${site} and saw possible opportunities around ${service.toLowerCase()}. If useful, I can share a few ideas here.`,
      "Mini audit": `Website: ${site}\nIndustry: ${niche}\nService: ${service}\nObservation: ${text(f.observation) || "[Add your verified observation]"}\nNext step: Share tailored recommendations and ask if a conversation would be useful.`,
    };
  }
  const purposeLine = {
    "Guest Post":
      "We can provide an original, well-researched article written to match your audience and editorial requirements.",
    "Link Insertion":
      "We would like to discuss a relevant link insertion within an existing article, where it naturally fits the content.",
    "Guest Post + Link Insertion":
      "We are open to a new guest post or a relevant link insertion, depending on your editorial policy.",
    "Long-term Partnership":
      "We are looking for reliable publishing partners for recurring placements.",
    "Price Inquiry":
      "Could you share your current publishing options, pricing, turnaround time and payment terms?",
  }[purpose];
  const closing =
    f.tone === "Short & Direct"
      ? "Please share your availability, rate, turnaround time and publishing requirements."
      : f.tone === "Friendly"
        ? "If you’re open to this, I’d be happy to work around your guidelines. Could you share the available options and rates?"
        : "If you are accepting collaborations, please share your guidelines, pricing, turnaround time and payment terms.";
  return {
    Subject: `${purpose} inquiry for ${site}`,
    Email: `${greeting}\n\nI came across ${site} while researching publishers in ${niche}. I’m reaching out about a possible content collaboration.\n\n${purposeLine}${text(f.offer) ? "\n\nA little more context: " + text(f.offer) : ""}\n\n${closing}\n\n${signature}`,
    "Follow-up 1": `${greeting}\n\nJust following up on my previous message regarding ${site}. If you are accepting ${purpose.toLowerCase()} opportunities, could you share your current pricing, requirements and turnaround time?\n\n${signature}`,
    "Follow-up 2": `${greeting}\n\nOne last quick follow-up regarding ${site}. We’re still interested in working with your publication and can adapt to your editorial requirements. Please send over the details if collaboration is available.\n\n${signature}`,
    LinkedIn: `Hi ${name || "there"}, I found ${site} while researching ${niche} publishers. I’m with ${company} and would like to connect about a possible ${purpose.toLowerCase()} collaboration.`,
    WhatsApp: `Hi ${name || "there"}, this is ${sender} from ${company}. Do you currently accept ${purpose.toLowerCase()} collaborations on ${site}? If yes, please share pricing, requirements and turnaround time. Thanks!`,
  };
}
