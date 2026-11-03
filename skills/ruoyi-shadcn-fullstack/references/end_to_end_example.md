# End-to-End CRUD Example: Village Resident Management

This walkthrough demonstrates the end-to-end creation of a business module called **Villagers (村民档案)** from SQL to Spring Boot to React Shadcn UI.

---

## 1. MySQL DDL (`sql/village_villager.sql`)

```sql
DROP TABLE IF EXISTS `village_villager`;
CREATE TABLE `village_villager` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(50) NOT NULL COMMENT '姓名',
  `id_card` varchar(18) NOT NULL COMMENT '身份证号',
  `gender` char(1) DEFAULT '0' COMMENT '性别（0男 1女）',
  `phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `grid_name` varchar(100) DEFAULT NULL COMMENT '所属网格',
  `household_id` varchar(64) DEFAULT NULL COMMENT '户籍编号',
  `political_status` varchar(20) DEFAULT '群众' COMMENT '政治面貌',
  `residence_status` varchar(20) DEFAULT '在村常住' COMMENT '常住状态',
  `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='村民档案表';
```

---

## 2. Spring Boot Entity (`VillageVillager.java`)

```java
package com.ruoyi.project.village.domain;

import com.ruoyi.framework.web.domain.BaseEntity;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;

public class VillageVillager extends BaseEntity {
    private static final long serialVersionUID = 1L;

    private Long id;
    private String name;
    private String idCard;
    private String gender;
    private String phone;
    private String gridName;
    private String householdId;
    private String politicalStatus;
    private String residenceStatus;
    private String status;
    private String delFlag;

    // Standard getters & setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getIdCard() { return idCard; }
    public void setIdCard(String idCard) { this.idCard = idCard; }
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    public String getGridName() { return gridName; }
    public void setGridName(String gridName) { this.gridName = gridName; }
    public String getHouseholdId() { return householdId; }
    public void setHouseholdId(String householdId) { this.householdId = householdId; }
    public String getPoliticalStatus() { return politicalStatus; }
    public void setPoliticalStatus(String politicalStatus) { this.politicalStatus = politicalStatus; }
    public String getResidenceStatus() { return residenceStatus; }
    public void setResidenceStatus(String residenceStatus) { this.residenceStatus = residenceStatus; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getDelFlag() { return delFlag; }
    public void setDelFlag(String delFlag) { this.delFlag = delFlag; }

    @Override
    public String toString() {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
            .append("id", getId())
            .append("name", getName())
            .append("idCard", getIdCard())
            .toString();
    }
}
```

---

## 3. Frontend Zod Schema (`schema.ts`)

```typescript
import { z } from 'zod'

export const villagerSchema = z.object({
  id: z.number().or(z.string()),
  name: z.string().min(2, '姓名至少2个字符'),
  idCard: z.string().regex(/(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, '请输入正确的二代身份证号'),
  gender: z.string().default('0'),
  phone: z.string().regex(/^1[3-9]\d{9}$/, '请输入正确的手机号码').optional().or(z.literal('')),
  gridName: z.string().min(1, '请选择所属网格'),
  householdId: z.string().optional(),
  politicalStatus: z.string().default('群众'),
  residenceStatus: z.string().default('在村常住'),
  createTime: z.string().optional(),
})

export type Villager = z.infer<typeof villagerSchema>

export const villagerFormSchema = villagerSchema.omit({ id: true, createTime: true })
export type VillagerFormValues = z.infer<typeof villagerFormSchema>
```

---

## 4. Frontend Mutate Dialog Component (`villager-mutate-dialog.tsx`)

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { villagerFormSchema, VillagerFormValues, Villager } from '../data/schema'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { useCreateVillagerMutation, useUpdateVillagerMutation } from '../api/villagers-api'

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialData?: Villager | null
}

export function VillagerMutateDialog({ open, onOpenChange, initialData }: Props) {
  const isEdit = Boolean(initialData)
  const createMutation = useCreateVillagerMutation()
  const updateMutation = useUpdateVillagerMutation()

  const form = useForm<VillagerFormValues>({
    resolver: zodResolver(villagerFormSchema),
    defaultValues: {
      name: initialData?.name || '',
      idCard: initialData?.idCard || '',
      phone: initialData?.phone || '',
      gridName: initialData?.gridName || '第1网格（东溪组）',
      politicalStatus: initialData?.politicalStatus || '群众',
      residenceStatus: initialData?.residenceStatus || '在村常住',
      gender: initialData?.gender || '0',
    },
  })

  const onSubmit = async (values: VillagerFormValues) => {
    if (isEdit && initialData) {
      await updateMutation.mutateAsync({ ...values, id: initialData.id })
    } else {
      await createMutation.mutateAsync(values)
    }
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='sm:max-w-lg'>
        <DialogHeader>
          <DialogTitle>{isEdit ? '编辑村民档案' : '录入新村民'}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-4'>
            <FormField
              control={form.control}
              name='name'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>姓名</FormLabel>
                  <FormControl>
                    <Input placeholder='例如：王福荣' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='idCard'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>身份证号码</FormLabel>
                  <FormControl>
                    <Input placeholder='18位二代身份证号码' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='phone'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>联系手机</FormLabel>
                  <FormControl>
                    <Input placeholder='11位常用手机号' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter className='gap-2 pt-2'>
              <Button type='button' variant='outline' onClick={() => onOpenChange(false)}>
                取消
              </Button>
              <Button type='submit' disabled={createMutation.isPending || updateMutation.isPending}>
                保存并提交
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
```
