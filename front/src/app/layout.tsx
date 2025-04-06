import "@mantine/core/styles.css";
import {
  ColorSchemeScript,
  mantineHtmlProps,
  MantineProvider,
} from "@mantine/core";
import AppLayout from "@/components/AppLayout";
import { StripeProvider } from "@/components/StripeProvider";
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
        <StripeProvider>
          <AppLayout>
            {children}
          </AppLayout>
        </StripeProvider>
      </MantineProvider>
      </body>
      </html>
  );
}
