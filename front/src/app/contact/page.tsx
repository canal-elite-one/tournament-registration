import ContactCard from "@/components/ContactCard";

export default function Page() {
  return (
      <ContactCard
          contactEmail={process.env.USKB_CONTACT_EMAIL}
          contactWebsite={process.env.USKB_WEBSITE}
          contactInsta={process.env.USKB_INSTA}
          contactLinkedIn={process.env.USKB_LINKED_IN}
      />
  );
}