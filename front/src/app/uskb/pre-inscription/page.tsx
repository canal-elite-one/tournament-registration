import PreRegisterForm from "@/app/uskb/pre-inscription/PreRegisterForm";

export default function PreRegisterPage() {
  return <PreRegisterForm password={process.env.PRE_REGISTER_PASSWORD || ''} />;
}
