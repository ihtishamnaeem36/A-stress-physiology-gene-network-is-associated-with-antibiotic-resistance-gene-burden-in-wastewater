const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
        Spacing, BorderStyle, ShadingType } = require("docx");
const fs = require("fs");

const NAVY = "1F3864";
const GRAY = "555555";
const ACCENT = "C00000";

function H1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 4 } },
    children: [new TextRun({ text, bold: true, color: NAVY, size: 28 })],
  });
}

function P(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 200, line: 320 },
    children: [new TextRun({ text, size: 24, color: opts.color || "222222", bold: opts.bold || false, italics: opts.italics || false })],
  });
}

function Bullet(text) {
  return new Paragraph({
    spacing: { after: 120, line: 300 },
    bullet: { level: 0 },
    children: [new TextRun({ text, size: 24, color: "222222" })],
  });
}

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1200, right: 1200 } } },
    children: [
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun({ text: "PROJECT 2.2 — PLAIN-LANGUAGE SUMMARY", bold: true, color: GRAY, size: 18, allCaps: true })],
      }),
      new Paragraph({
        spacing: { after: 40 },
        children: [new TextRun({ text: "What this study did, and what it found", bold: true, color: NAVY, size: 40 })],
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new TextRun({ text: "Written for a general reader — no background in genetics, statistics, or microbiology needed.", italics: true, color: GRAY, size: 22 })],
      }),

      H1("The short version"),
      P("We looked at the DNA of the whole community of bacteria living in wastewater from hospitals, homes, and a slaughterhouse in three Pakistani cities. We were not looking for antibiotic-resistant bacteria directly. Instead, we looked at genes bacteria use to cope with stress — things like DNA damage, oxygen damage, and running low on nutrients. We found that these stress-coping genes rise and fall together, as if they were parts of one connected system. Then we checked whether that system had anything to do with antibiotic resistance, and one part of it — the genes bacteria switch on when they are struggling to survive — tracked closely with how much antibiotic-resistance DNA was in the same water. The worse the stress response, the more resistance genes were present, across many different types of antibiotics."),

      H1("What we actually did"),
      P("We collected 18 wastewater samples: from hospitals, community sewage, and a slaughterhouse, across three cities. Instead of growing bacteria in a lab, we sequenced all the DNA in each sample directly — this is called metagenomics. It lets you see the genetic material of an entire microbial community at once, without needing to isolate any single species."),
      P("From that DNA, we measured how abundant roughly 200 specific \"stress-response\" genes were in each sample. We grouped these genes into 15 functional groups (for example: genes for repairing DNA, genes for handling toxic oxygen molecules, genes for pausing growth when nutrients run low) based on what job they do inside a bacterial cell."),

      H1("Finding 1 — the stress genes form one connected system"),
      P("When a gene group goes up in a sample, do the other gene groups go up too, or does each behave independently? We tested every pair of gene groups against each other and built a map (a network) of which groups move together. The result: almost all 15 groups are connected to each other in a single, tightly linked web, rather than behaving as separate, unrelated systems. This suggests that when bacteria in wastewater are under stress, many of their defense systems switch on together, as a coordinated response, not as isolated reactions."),

      H1("Finding 2 — one gene group tracks antibiotic resistance"),
      P("Separately, we obtained a measurement of antibiotic-resistance genes for the same 18 samples, covering 21 major categories of antibiotics (things like penicillin-type drugs, sulfa drugs, and drugs of last resort used against multidrug-resistant infections)."),
      P("We then asked: does the amount of resistance DNA in a sample line up with any of the 15 stress-gene groups? For 14 of the 15 groups, the answer was no — no meaningful relationship. But one group stood out: the \"stringent response,\" the set of genes bacteria use to power down and survive when they are starved or under attack. In samples where the stringent-response genes were more active, resistance genes were also higher — and this held up across many different antibiotic classes at once (including multidrug resistance, sulfa drugs, aminoglycosides, penicillin-type drugs, and others), not just one. We double-checked this with several different methods, including re-running the test after removing each sample one at a time, and the pattern held every time — this was not caused by one unusual sample skewing the result."),
      P("As expected from where they came from, hospital wastewater carried substantially more antibiotic-resistance DNA overall than community or slaughterhouse wastewater — roughly two-to-three times as much."),

      H1("Why this might matter"),
      P("It suggests that a bacterial community's stress-survival machinery and its antibiotic-resistance load are not independent of each other — they seem to move together. If that holds up in future, larger studies, it raises the possibility of using a general stress-response signal as an early warning sign for resistance risk in wastewater, without needing to test for resistance genes directly every time. That would be useful because monitoring for stress-response activity is simpler and cheaper than screening for dozens of specific resistance genes one by one."),

      H1("What this is not saying"),
      Bullet("This is not proof that stress causes resistance, or that resistance causes stress. We found that the two rise and fall together — we did not prove which one drives the other, or whether something else drives both."),
      Bullet("The study is based on 18 samples from three cities. That is enough to find a real, statistically solid pattern, but it is too small to say this pattern is true everywhere, in every city or country."),
      Bullet("We measured whole community DNA, not the DNA of individual bacterial species. It is possible that a single type of bacteria that happens to be both stressed and resistant is behind part of this pattern, rather than every species independently doing both. Confirming this would need additional work identifying which species carry which genes."),
      Bullet("This was done once, at one point in time, in each location. We do not yet know whether the pattern would look the same at a different time of year or a different place."),

      H1("In one sentence"),
      P("Bacteria in wastewater that are working hardest to survive stress also tend to carry the most antibiotic-resistance genes, and this connection is strong enough, and consistent enough across drug types, that it is unlikely to be a coincidence.", { bold: true, color: ACCENT }),

      new Paragraph({
        spacing: { before: 300 },
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: "AAAAAA", space: 8 } },
        children: [new TextRun({ text: "This summary accompanies the full manuscript \"A stress-physiology gene co-occurrence network is associated with antibiotic-resistance-gene burden in urban wastewater metagenomes\" (Project22_FINAL_Manuscript.docx), where every number here is reported in full with statistical detail.", italics: true, color: GRAY, size: 20 })],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/sessions/quirky-amazing-cori/mnt/outputs/manuscript/Plain_Language_Summary.docx", buf);
  console.log("done");
});
