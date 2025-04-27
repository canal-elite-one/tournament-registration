import {
  DefaultApi,
  type SetCategoryInput
} from "@/backend_api/backend";
import {NextResponse} from "next/server";
import {CategoryForm} from "@/app/admin/categories/page";

export async function POST(req: Request) {
  try {
    const {categories} = await req.json();

    const api = new DefaultApi();

    const body: SetCategoryInput = {
        categories: categories.map((c: CategoryForm) => {
          return {
            categoryId: c.id,
            alternateName: c.alternateName,
            color: c.color === "" ? null : c.color,
            minPoints: c.minPoints,
            maxPoints: c.maxPoints,
            startTime: new Date(c.startTime),
            womenOnly: c.womenOnly,
            baseRegistrationFee: c.entryFee,
            lateRegistrationFee: c.lateFee,
            rewardFirst: c.rewardFirst,
            rewardSecond: c.rewardSecond,
            rewardSemi: c.rewardSemi,
            rewardQuarter: c.rewardQuarter,
            maxPlayers: c.maxPlayers,
            overbookingPercentage: c.overbookingPercentage,
          }
        })
    }

    const response = await api.setCategories({setCategoryInput: body});

    return NextResponse.json({body: response}, {status: 200});
  } catch (error) {
    console.error(error);
    return NextResponse.json(
        {error: 'An error occurred on categories submission.'},
        {status: 500}
    );
  }
}