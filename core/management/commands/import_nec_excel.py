# -*- coding: utf-8 -*-
"""
Management command to import NEC Asset Register Excel file.
Usage: python manage.py import_nec_excel /path/to/file.xlsx

Delegates to core.excel_importer for all parsing logic.
"""
from django.core.management.base import BaseCommand
from core.excel_importer import import_lists, import_fixed_assets


class Command(BaseCommand):
    help = 'Import NEC Asset Registration Excel into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        self.stdout.write(self.style.SUCCESS(f'Importing from: {file_path}'))

        # Import reference lists first
        import_lists(file_path, stdout=self.stdout)

        # Import fixed assets
        result = import_fixed_assets(file_path, stdout=self.stdout)

        self.stdout.write(self.style.SUCCESS(
            f'\nFixed Assets: {result["imported"]} imported, {result["skipped"]} skipped'
        ))
        if result.get('errors'):
            for aid, name, err in result['errors'][:5]:
                self.stdout.write(self.style.WARNING(f'  Failed: {aid} - {name}: {err}'))

        self.stdout.write(self.style.SUCCESS('\n=== Import Complete ==='))
