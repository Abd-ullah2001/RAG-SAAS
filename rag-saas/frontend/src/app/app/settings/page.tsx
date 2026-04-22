"use client";

import { useState } from "react";
import { User, CreditCard, Bell, Shield, LogOut } from "lucide-react";
import { Btn, Inp, Toggle } from "@/components/ui/shared";

export default function Settings() {
  const [tab, setTab] = useState("profile");
  const [emailNotifs, setEmailNotifs] = useState(true);
  const [mfa, setMfa] = useState(false);

  return (
    <div>
      <div className="pghdr">
        <h1 className="pgtit">Settings</h1>
        <p className="pgsub">Manage your account settings and preferences.</p>
      </div>

      <div className="sec">
        <div className="stabs">
          <button className={`stab${tab === "profile" ? " on" : ""}`} onClick={() => setTab("profile")}><User size={14} style={{ display: "inline", marginBottom: -2, marginRight: 6 }} /> Profile</button>
          <button className={`stab${tab === "billing" ? " on" : ""}`} onClick={() => setTab("billing")}><CreditCard size={14} style={{ display: "inline", marginBottom: -2, marginRight: 6 }} /> Billing</button>
          <button className={`stab${tab === "notifications" ? " on" : ""}`} onClick={() => setTab("notifications")}><Bell size={14} style={{ display: "inline", marginBottom: -2, marginRight: 6 }} /> Notifications</button>
          <button className={`stab${tab === "security" ? " on" : ""}`} onClick={() => setTab("security")}><Shield size={14} style={{ display: "inline", marginBottom: -2, marginRight: 6 }} /> Security</button>
        </div>

        <div className="card p24" style={{ maxWidth: 600 }}>
          {tab === "profile" && (
            <div>
              <div className="w6 mb20">Personal Information</div>
              <div className="fgrp">
                <label className="flabel">Full Name</label>
                <Inp defaultValue="Alex Johnson" />
              </div>
              <div className="fgrp">
                <label className="flabel">Email Address</label>
                <Inp defaultValue="alex@company.com" disabled />
                <div className="xs tm mt4">To change your email, please contact support.</div>
              </div>
              <Btn v="p" className="mt12">Save Changes</Btn>
            </div>
          )}

          {tab === "billing" && (
            <div>
              <div className="w6 mb20">Current Plan</div>
              <div className="card p16 mb20" style={{ background: "var(--s2)" }}>
                <div className="fx jb ic">
                  <div>
                    <div className="w6 cy">Pro Plan</div>
                    <div className="xs tm mt4">$49 / month</div>
                  </div>
                  <Btn v="s" sm>Manage Billing</Btn>
                </div>
              </div>
              <div className="w6 mb12">Payment Method</div>
              <div className="fx ic gap12 mb20 p16 r8" style={{ border: "1px solid var(--b)" }}>
                <div style={{ width: 40, height: 26, background: "var(--s1)", border: "1px solid var(--b)", borderRadius: 4, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700 }}>VISA</div>
                <div className="f1">
                  <div className="sm2 w5">Visa ending in 4242</div>
                  <div className="xs tm">Expires 12/2026</div>
                </div>
              </div>
            </div>
          )}

          {tab === "notifications" && (
            <div>
              <div className="w6 mb20">Email Notifications</div>
              <div className="fx jb ic mb20">
                <div>
                  <div className="sm2 w5">Usage Alerts</div>
                  <div className="xs tm">Get notified when you reach 80% of your quota.</div>
                </div>
                <Toggle on={emailNotifs} onToggle={() => setEmailNotifs(!emailNotifs)} />
              </div>
              <div className="fx jb ic">
                <div>
                  <div className="sm2 w5">Product Updates</div>
                  <div className="xs tm">Occasional emails about new features.</div>
                </div>
                <Toggle on={false} onToggle={() => {}} />
              </div>
            </div>
          )}

          {tab === "security" && (
            <div>
              <div className="w6 mb20">Security Preferences</div>
              <div className="fx jb ic mb24 p16 r8" style={{ border: "1px solid var(--b)", background: "var(--s2)" }}>
                <div>
                  <div className="sm2 w5">Two-Factor Authentication</div>
                  <div className="xs tm mt4">Add an extra layer of security to your account.</div>
                </div>
                <Btn v={mfa ? "s" : "p"} sm onClick={() => setMfa(!mfa)}>
                  {mfa ? "Disable" : "Enable 2FA"}
                </Btn>
              </div>
              <div className="hr mb24" />
              <div className="w6 er mb12">Danger Zone</div>
              <div className="xs tm mb16">Once you delete your account, there is no going back. Please be certain.</div>
              <Btn v="d"><LogOut size={14} /> Delete Account</Btn>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
