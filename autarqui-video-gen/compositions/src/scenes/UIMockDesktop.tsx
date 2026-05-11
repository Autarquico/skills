/**
 * UIMockDesktop — Generic desktop SaaS UI mock for product demos.
 *
 * Tokenized version of the SigmaWeb desktop pattern.
 * Three regions: sidebar (left), top bar (header), content area.
 */

import * as React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface UIMockDesktopProps {
  app_name: string;
  logo_glyph?: string;
  logo_path?: string;
  /** Sidebar menu items */
  menu_items: string[];
  active_menu_index?: number;
  /** Top breadcrumb chip */
  empresa_label?: string;
  empresa_name?: string;
  /** Search bar */
  search_text?: string;
  search_placeholder?: string;
  search_active?: boolean;
  /** User chip (right side of top bar) */
  user_avatar_text?: string;
  user_email?: string;
  /** KPI cards — horizontal row */
  kpi_cards?: Array<{ value: string; label: string; accent?: string }>;
  /** Optional content card (e.g. empresa_card) */
  empresa_card?: {
    initials: string;
    name: string;
    nif: string;
    badge?: string;
  };
  fonts: LoadedFonts;
}

export const UIMockDesktop: React.FC<UIMockDesktopProps> = ({
  app_name,
  logo_glyph,
  logo_path,
  menu_items,
  active_menu_index = 0,
  empresa_label = "EMPRESA",
  empresa_name,
  search_text,
  search_placeholder = "¿En qué puedo ayudarte?",
  search_active = false,
  user_avatar_text,
  user_email,
  kpi_cards = [],
  empresa_card,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const op = fadeIn(frame, 0, 18);
  const accent = t.colors.accent[0]?.hex || "#a3d9a5";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        display: "flex",
        flexDirection: "row",
        opacity: op,
      }}
    >
      {/* SIDEBAR */}
      <div
        style={{
          width: 280,
          height: "100%",
          borderRight: `1px solid ${t.colors.ruleSoft}`,
          padding: "32px 0",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 32px 36px 32px" }}>
          {logo_path ? (
            <Img src={staticFile(logo_path)} style={{ width: 36, height: 36 }} />
          ) : logo_glyph ? (
            <div
              style={{
                fontFamily: fonts.displayItalic,
                fontStyle: "italic",
                fontWeight: 500,
                fontSize: 36,
                color: t.colors.heading,
                lineHeight: 1,
                width: 32,
                textAlign: "center",
              }}
            >
              {logo_glyph}
            </div>
          ) : null}
          <div
            style={{
              fontFamily: fonts.body,
              fontWeight: 500,
              fontSize: 16,
              color: t.colors.heading,
              letterSpacing: "0.18em",
            }}
          >
            {app_name}
          </div>
        </div>
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 11,
            letterSpacing: "0.18em",
            color: t.colors.faint,
            padding: "0 32px 12px 32px",
          }}
        >
          MENÚ
        </div>
        {menu_items.map((label, i) => {
          const isActive = i === active_menu_index;
          return (
            <div
              key={label}
              style={{
                padding: "14px 32px",
                fontFamily: fonts.body,
                fontWeight: isActive ? 500 : 400,
                fontSize: 16,
                color: isActive ? t.colors.heading : t.colors.muted,
                backgroundColor: isActive ? t.colors.surface : "transparent",
                borderLeft: isActive ? `2px solid ${t.colors.heading}` : "2px solid transparent",
                display: "flex",
                alignItems: "center",
                gap: 14,
              }}
            >
              <div
                style={{
                  width: 18,
                  height: 18,
                  border: `1.5px solid ${isActive ? t.colors.heading : t.colors.muted}`,
                  borderRadius: 3,
                }}
              />
              {label}
            </div>
          );
        })}
      </div>

      {/* MAIN COLUMN */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* TOP BAR */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 24,
            padding: "20px 32px",
            borderBottom: `1px solid ${t.colors.ruleSoft}`,
          }}
        >
          {empresa_name && (
            <div
              style={{
                backgroundColor: hexToA(accent, 0.2),
                borderRadius: 999,
                padding: "8px 16px",
                fontFamily: fonts.body,
                fontWeight: 400,
                fontSize: 13,
                color: t.colors.ink,
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <span style={{ color: t.colors.muted, letterSpacing: "0.14em", fontSize: 10, fontWeight: 500 }}>
                {empresa_label}
              </span>
              <span style={{ fontFamily: fonts.displayItalic, fontStyle: "italic", fontWeight: 500 }}>
                {empresa_name}
              </span>
            </div>
          )}
          <div
            style={{
              flex: 1,
              maxWidth: 720,
              backgroundColor: t.colors.surface,
              borderRadius: 999,
              border: `1px solid ${search_active ? t.colors.muted : t.colors.ruleSoft}`,
              padding: "12px 22px",
              fontFamily: fonts.body,
              fontWeight: 400,
              fontSize: 15,
              color: search_text ? t.colors.ink : t.colors.faint,
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <div style={{ color: t.colors.muted, fontSize: 16 }}>★</div>
            {search_text || search_placeholder}
            {search_active && (
              <span
                style={{
                  marginLeft: 2,
                  width: 2,
                  height: 18,
                  backgroundColor: t.colors.ink,
                  display: "inline-block",
                }}
              />
            )}
          </div>
          {(user_avatar_text || user_email) && (
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              {user_avatar_text && (
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: "50%",
                    backgroundColor: hexToA(accent, 0.2),
                    color: getDeepInk(accent),
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: fonts.body,
                    fontWeight: 500,
                    fontSize: 12,
                  }}
                >
                  {user_avatar_text}
                </div>
              )}
              {user_email && (
                <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 14, color: t.colors.ink }}>
                  {user_email}
                </div>
              )}
            </div>
          )}
        </div>

        {/* CONTENT */}
        <div style={{ flex: 1, padding: "32px 40px", position: "relative" }}>
          {kpi_cards.length > 0 && (
            <div style={{ display: "flex", gap: 20, marginBottom: 32 }}>
              {kpi_cards.map((card, i) => (
                <KpiD key={i} card={card} t={t} fonts={fonts} accent={accent} />
              ))}
            </div>
          )}

          {empresa_card && (
            <>
              <div
                style={{
                  fontFamily: fonts.display,
                  fontWeight: 600,
                  fontSize: 24,
                  color: t.colors.heading,
                  marginBottom: 18,
                }}
              >
                Empresas
              </div>
              <div
                style={{
                  border: `1px solid ${t.colors.ruleSoft}`,
                  borderRadius: 8,
                  padding: "22px 26px",
                  maxWidth: 460,
                  backgroundColor: t.colors.bg,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
                  <div
                    style={{
                      width: 56,
                      height: 56,
                      borderRadius: 8,
                      backgroundColor: t.colors.surface,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: fonts.displayItalic,
                      fontStyle: "italic",
                      fontWeight: 500,
                      fontSize: 22,
                      color: t.colors.ink,
                    }}
                  >
                    {empresa_card.initials}
                  </div>
                  {empresa_card.badge && (
                    <div
                      style={{
                        backgroundColor: hexToA(accent, 0.25),
                        color: getDeepInk(accent),
                        fontFamily: fonts.body,
                        fontWeight: 500,
                        fontSize: 10,
                        letterSpacing: "0.16em",
                        padding: "5px 10px",
                        borderRadius: 999,
                      }}
                    >
                      {empresa_card.badge}
                    </div>
                  )}
                </div>
                <div style={{ borderTop: `1px solid ${t.colors.ruleSoft}`, paddingTop: 16 }}>
                  <div
                    style={{
                      fontFamily: fonts.display,
                      fontWeight: 600,
                      fontSize: 22,
                      color: t.colors.heading,
                      marginBottom: 6,
                    }}
                  >
                    {empresa_card.name}
                  </div>
                  <div style={{ fontFamily: fonts.body, fontWeight: 400, fontSize: 13, color: t.colors.muted }}>
                    {empresa_card.nif}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const KpiD: React.FC<{
  card: { value: string; label: string; accent?: string };
  t: ReturnType<typeof useStyleTokens>;
  fonts: LoadedFonts;
  accent: string;
}> = ({ card, t, fonts, accent }) => {
  const cardAccent = card.accent ?? t.colors.rule;
  return (
    <div
      style={{
        flex: 1,
        maxWidth: 280,
        border: `1px solid ${t.colors.ruleSoft}`,
        borderTop: `3px solid ${cardAccent}`,
        borderRadius: 8,
        padding: "22px 24px",
        backgroundColor: t.colors.bg,
      }}
    >
      <div
        style={{
          width: 38,
          height: 38,
          borderRadius: 8,
          backgroundColor: cardAccent === t.colors.rule ? t.colors.surface : hexToA(cardAccent, 0.2),
          marginBottom: 22,
        }}
      />
      <div
        style={{
          fontFamily: fonts.displayItalic,
          fontStyle: "italic",
          fontWeight: 500,
          fontSize: 38,
          color: t.colors.heading,
          lineHeight: 1,
          marginBottom: 10,
        }}
      >
        {card.value}
      </div>
      <div style={{ fontFamily: fonts.body, fontWeight: 400, fontSize: 14, color: t.colors.muted }}>
        {card.label}
      </div>
    </div>
  );
};

function hexToA(hex: string, alpha: number): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function getDeepInk(hex: string): string {
  const h = hex.replace("#", "");
  const r = Math.max(0, parseInt(h.slice(0, 2), 16) - 70);
  const g = Math.max(0, parseInt(h.slice(2, 4), 16) - 50);
  const b = Math.max(0, parseInt(h.slice(4, 6), 16) - 70);
  return `rgb(${r},${g},${b})`;
}

export const UIMockDesktopSchema = {
  app_name: { type: "string", required: true },
  logo_glyph: { type: "string", required: false },
  logo_path: { type: "string", required: false },
  menu_items: { type: "array", required: true, of: "string" },
  active_menu_index: { type: "number", required: false },
  empresa_label: { type: "string", required: false },
  empresa_name: { type: "string", required: false },
  search_text: { type: "string", required: false },
  search_placeholder: { type: "string", required: false },
  search_active: { type: "boolean", required: false },
  user_avatar_text: { type: "string", required: false },
  user_email: { type: "string", required: false },
  kpi_cards: { type: "array", required: false, of: "object" },
  empresa_card: { type: "object", required: false },
} as const;
