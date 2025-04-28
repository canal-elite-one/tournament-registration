"use client";

import {useRouter} from "next/navigation";
import {useForm} from "@mantine/form";
import {Button, PasswordInput, Stack, TextInput} from "@mantine/core";

export default function PreRegisterForm({password}: { password: string; }) {

  const router = useRouter();

  const form = useForm({
    initialValues: {
      licenceNo: '',
      password: '',
    },
  });

  const handleSubmit = (values: { licenceNo: string; password: string }) => {
    if (values.password === password) {
      router.push(`/joueur/${values.licenceNo}`);
    } else {
      form.setFieldError('password', 'Incorrect password');
    }
  };

  return (
      <div className="flex justify-center items-center min-h-screen">
        <form
            onSubmit={form.onSubmit(handleSubmit)}
            className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md"
        >
          <Stack>
            <TextInput
                label="Numéro de licence"
                placeholder="Rentrez votre numéro de licence"
                {...form.getInputProps('licenceNo')}
            />
            <PasswordInput
                label="Mot de passe"
                placeholder="Entrer le mot de passe du club"
                {...form.getInputProps('password')}
            />
            <Button type="submit" fullWidth>
              Submit
            </Button>
          </Stack>
        </form>
      </div>
  );
}