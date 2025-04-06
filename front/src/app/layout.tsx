import "@mantine/core/styles.css";
import {
  ColorSchemeScript,
  mantineHtmlProps,
  MantineProvider,
} from "@mantine/core";
import AppLayout from "@/components/AppLayout";
import "./globals.css";


export default async function RootLayout({
                                           children,
                                         }: {
  children: React.ReactNode;
}) {

  return (
      <html lang="fr" {...mantineHtmlProps}>
      <head>
        <ColorSchemeScript/>
      </head>
      <body>
      <MantineProvider>
        <AppLayout>
          {children}
        </AppLayout>
      </MantineProvider>
      </body>
      </html>
  );
}
