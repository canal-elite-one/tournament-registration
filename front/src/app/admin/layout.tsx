import "@mantine/core/styles.css";
import {
  MantineProvider,
  ColorSchemeScript,
  mantineHtmlProps,
} from "@mantine/core";
import SessionWrapper from "@/components/SessionWrapper";
import "../globals.css";
import AdminAppLayout from "@/components/AdminAppLayout";

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
          <AdminAppLayout>
            {children}
          </AdminAppLayout>
        </MantineProvider>
      </SessionWrapper>
      </body>
      </html>
  );
}
