"use client";

import { useState } from "react";
import Image from "next/image";

import { Dialog, DialogContent } from "@/components/ui/dialog";
import type { FileOut } from "@/lib/types";
import { MEDIA_BASE_URL } from "@/lib/config";

const FILE_TYPE_LABELS: Record<string, string> = {
  METER_PHOTO: "Есептеу құралы",
  GAS_LEAK_PHOTO: "Газ шығу орны",
  OTHER: "Сурет",
};

function fullUrl(storageUrl: string): string {
  return storageUrl.startsWith("http") ? storageUrl : `${MEDIA_BASE_URL}${storageUrl}`;
}

export function PhotoGallery({ files }: { files: FileOut[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  if (files.length === 0) {
    return <p className="text-sm text-muted-foreground">Фотосуреттер жоқ.</p>;
  }

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {files.map((file, index) => (
          <button
            key={file.id}
            onClick={() => setOpenIndex(index)}
            className="group relative aspect-square overflow-hidden rounded-lg border bg-muted"
          >
            <Image
              src={fullUrl(file.storage_url)}
              alt={FILE_TYPE_LABELS[file.file_type] || "Сурет"}
              fill
              className="object-cover transition-transform group-hover:scale-105"
              unoptimized
            />
            <span className="absolute bottom-0 left-0 right-0 bg-black/60 px-2 py-1 text-[11px] text-white">
              {FILE_TYPE_LABELS[file.file_type] || file.file_type}
            </span>
          </button>
        ))}
      </div>

      <Dialog open={openIndex !== null} onOpenChange={(open) => !open && setOpenIndex(null)}>
        <DialogContent className="max-w-3xl border-none bg-transparent p-0 shadow-none">
          {openIndex !== null && (
            <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
              <Image
                src={fullUrl(files[openIndex].storage_url)}
                alt={FILE_TYPE_LABELS[files[openIndex].file_type] || "Сурет"}
                fill
                className="object-contain"
                unoptimized
              />
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
