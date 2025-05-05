import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/notifications/styles.css";
import "../globals.css";

import {
  MantineProvider,
  ColorSchemeScript,
  mantineHtmlProps,
} from "@mantine/core";

import SessionWrapper from "@/components/SessionWrapper";
import AdminAppLayout from "@/components/AdminAppLayout";
import {Notifications} from "@mantine/notifications";

export const metadata = {
  title: "Admin Dashboard",
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
      <html lang="fr" {...mantineHtmlProps}>
      <head>
        <ColorSchemeScript />
      </head>
      <body>
      <SessionWrapper>
        <MantineProvider>
          <Notifications position="top-right" autoClose={30000}/>
          <AdminAppLayout>{children}</AdminAppLayout>
        </MantineProvider>
      </SessionWrapper>
      </body>
      </html>
  );
}
